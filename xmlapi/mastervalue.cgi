#!/bin/tclsh
load tclrega.so
load tclrpc.so
puts -nonewline {Content-Type: text/xml
Access-Control-Allow-Origin: *

<?xml version="1.0" encoding="ISO-8859-1" ?><mastervalue>}

set device_id ""
set channel_id ""
set datapoint_id ""
set requested_names ""
set allMasterValues ""
set tcpport "2001"

catch {
	set input $env(QUERY_STRING)
	set pairs [split $input &]
	foreach pair $pairs {
		if {0 != [regexp "^(\[^=]*)=(.*)$" $pair dummy varname val]} {
			set $varname $val
		}
	}
}

set devids [split $device_id ,]
if { $requested_names == "" } {
	set allMasterValues "*"
} else {
	set requestedNames [split $requested_names ,]
}

foreach devid $devids {
	array set values [rega_script {
		integer iseId = "} $devid {";
		var oDevice = dom.GetObject(iseId);
		var address = oDevice.Address();
		var deviceType = oDevice.HssType();
		Write("<device");
		Write(" name='");
		WriteXML(oDevice.Name());
		Write("'");
		Write(" ise_id='" # iseId # "'");
		Write(" device_type='");
		WriteXML(deviceType);                                         
		Write("'");                                                   
		Write(" >");                                                  
	}]
	set deviceAddress $values(address)           
	set deviceType $values(deviceType)           

	puts -nonewline $values(STDOUT)              

	if {$deviceType=="HM-CC-VG-1"} {             
		set ausgabe [xmlrpc http://127.0.0.1:9292/groups getParamset [list string $deviceAddress] [list string "MASTER"] ]
	} else {                                                                                                                  
		set ausgabe [xmlrpc http://127.0.0.1:$tcpport/ getParamset [list string $deviceAddress] [list string "MASTER"] ]      
	}                                                                                                                         

	foreach { bezeichnung wert } $ausgabe {                                                                                   
		if { ($allMasterValues == "*" || [lsearch $requestedNames $bezeichnung] >= 0) } {                                 
			puts -nonewline {<mastervalue name='}                                                                     
			puts -nonewline $bezeichnung                                                                              
			puts -nonewline {' value='}                                                                               
			puts -nonewline $wert                                                                                     
			puts -nonewline {'/>}                                                                                     
		}                                                                                                                 
	}                                                                                                                     
	puts -nonewline {</device>}                                                                                               
}                                                                                                                                 
puts -nonewline {</mastervalue>}
