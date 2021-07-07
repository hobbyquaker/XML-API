#!/bin/tclsh
load tclrega.so
puts -nonewline {Content-Type: text/xml
Access-Control-Allow-Origin: *

<?xml version="1.0" encoding="ISO-8859-1" ?><state>}

set device_id ""
set channel_id ""
set datapoint_id ""

catch {
	set input $env(QUERY_STRING)
	set pairs [split $input &]
	foreach pair $pairs {
		if {0 != [regexp "^(\[^=]*)=(.*)$" $pair dummy varname val]} {
   			set $varname $val
   		}
	}
}

array set res [rega_script {

	string sDevIds = "} $device_id {";
	string sChannelIds = "} $channel_id {";
	string sDatapointIds = "} $datapoint_id {";
	string sChnId;
	string sDPId;

	if (sDatapointIds.Length() > 0 ) {
	  
		string sDatapointId;
		foreach(sDatapointId, sDatapointIds.Split(",")) {	
					
			object oDatapoint = dom.GetObject(sDatapointId);
        	   	if (oDatapoint.IsTypeOf(OT_DP)){
           			Write("<datapoint ise_id='");
           			WriteXML(sDatapointId);
	               		Write("' value='"); 
        	       		WriteXML(oDatapoint.Value());
               			Write("'/>");
           		} 
        
		}
		
	} else {
		
		if (sChannelIds.Length() > 0 ) {

			string sChannelId;
			foreach(sChannelId, sChannelIds.Split(",")) {		
				object oChannel2 = dom.GetObject(sChannelId);		
				
				if (sDevIds.Length() > 0 ) {
					sDevIds = sDevIds # "," # oChannel2.Device().ToString();
				} else {
					sDevIds = oChannel2.Device().ToString();
				}
			}	
		}			

		string sDevId;
		foreach(sDevId, sDevIds.Split(",")) {
			
			object oDevice = dom.GetObject(sDevId);

			if(oDevice.ReadyConfig() && (oDevice.Name() != "Zentrale") && (oDevice.Name() != "HMW-RCV-50 BidCoS-Wir") && oDevice.IsTypeOf(OT_DEVICE)) {
				Write("<device");
				Write(" name='" # oDevice.Name() # "'");
				Write(" ise_id='" # sDevId # "'");

				string interfaceid = oDevice.Interface();
				string servicechan = "" # dom.GetObject(interfaceid).Name() #"."#oDevice.Address()#":0";
				object schan = dom.GetObject(servicechan#".UNREACH");
				if(schan) { Write(" unreach='" # schan.Value() #"'"); }
				object schan = dom.GetObject(servicechan#".STICKY_UNREACH");
				if(schan) { Write(" sticky_unreach='" # schan.Value() #"'"); }
				object schan = dom.GetObject(servicechan#".CONFIG_PENDING");
				if(schan) { Write(" config_pending='" # schan.Value() #"'"); }

				Write(" >");  ! device tag schliessen

				foreach(sChnId, oDevice.Channels())	{
					object oChannel = dom.GetObject(sChnId);
					if ((!oChannel.Internal()) || oChannel.Internal()) {

						Write("<channel name='");
						WriteXML( oChannel.Name() );
						Write("' ise_id='" # sChnId # "'>");

						foreach(sDPId, oChannel.DPs().EnumUsedIDs()) {
							object oDP = dom.GetObject(sDPId);
							if(oDP) {
								string dp = oDP.Name().StrValueByIndex(".", 2);

								if( (dp != "ON_TIME") && (dp != "INHIBIT") && (dp != "CMD_RETS") && (dp != "CMD_RETL") && (dp != "CMD_SETS") && (dp != "CMD_SETL") ) {
									Write("<datapoint");
									Write(" name='"); WriteXML(oDP.Name());
									Write("' type='"); WriteXML(oDP.Name().StrValueByIndex(".", 2));
									Write("' ise_id='" # sDPId );
									! state fragt den aktuellen status des sensors/aktors ab, dauert lange
									!Write("' state='"); WriteXML(oDP.State());
									! value nimmt den von der ccu gecachten wert, moeglicherweise nicht korrekt. Ggf. bei einigen geraeten immer abfragen
									Write("' value='"); WriteXML(oDP.Value());
									Write("' valuetype='" # oDP.ValueType());
									Write("' valueunit='" # oDP.ValueUnit());
									Write("' timestamp='" # oDP.Timestamp().ToInteger());
									Write("' lastdpactiontime='" # oDP.LastDPActionTime().ToInteger());
									Write("' />");
								}
							}
						}
						Write("</channel>");
					}
				}
				Write("</device>");
			}
		}	
	}
}]
puts -nonewline $res(STDOUT)
puts -nonewline {</state>}
