caput test_epics:AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:EnableRampTrigger 1
caput test_epics:AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:RampStartMode 1
caput test_epics:AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:streamEnable 1
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AxiSy56040:OutputConfig[1] 0
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:Enable 1
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:DestSel 0x20000
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:RateSel 5
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2TriggerReg[0]:Enable 1
caput test_epics:AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2TriggerReg[0]:Width 10

