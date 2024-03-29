def rpclayout(i, p, *rows): i["RPC/Layouts/" + p] = DQMItem(layout=rows)

########### define varialbles for frequently used strings #############
rpclink = '   >>> <a href="https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftRPC">Description</a>'

rpcevents = "Events processed by the RPC DQM"
fed = "FED Fatal Errors"
top = "RPC TOP Summary Histogram <br><font color=green><b>GREEN</b> - Good Chamber </font><br> <font color=blue><b>BLUE</b> - Chamber OFF</font><br> <font color=yellow><b>YELLOW</b> - Noisy Strip </font><br> <font color=orange><b>ORANGE</b> - Noisy Chamber </font><br> <font color=pink><b>PINK</b> - Partly Dead Chamber </font><br> <font color=red><b>RED</b> - Fully Dead Chamber </font><br> <font color=aqua><b>LIGHT BLUE</b> - Bad Occupancy Shape </font> <br>"
occupancy = "Occupancy "
clsize = "Cluster Size of RPC system"
nrofcl = "Number of Clusters "
nrofdigi = "Number of Digi"
eff = "Efficiency"
bx  = "RPC BX distribution "

################### Links to TOP Summary Histograms #################################
#FED Fatal
rpclayout(dqmitems, "01-Fatal_FED_Errors",
          [{ 'path': "RPC/FEDIntegrity/FEDFatal", 'description': fed + rpclink }])
##-------------------

#RPC Events
rpclayout(dqmitems, "02-RPC_Events",
          [{ 'path': "RPC/Noise/RPCEvents", 'description': rpcevents + rpclink }])
##-------------------

#RPC Events
rpclayout(dqmitems, "03-RPC_HV_Status",
          [{ 'path': "RPC/DCSInfo/rpcHV", 'description': rpcevents + rpclink }])
##-------------------

#Roll Quality

rpclayout(dqmitems, "04-Barrel_TOP_summary_Distribution",
          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Wheel2", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Wheel1", 'description': top + rpclink  }],

          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Wheel0", 'description': top + rpclink  },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Wheel-1", 'description': top + rpclink  },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Wheel-2", 'description': top + rpclink  }]
          )

rpclayout(dqmitems, "05-Barrel_TOP_Summary",
          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Roll_vs_Sector_Wheel2", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Roll_vs_Sector_Wheel1", 'description': top + rpclink }],

          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Roll_vs_Sector_Wheel0", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Roll_vs_Sector_Wheel-1", 'description': top + rpclink},
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Roll_vs_Sector_Wheel-2", 'description': top + rpclink}]
          )

rpclayout(dqmitems, "06-EndCap_TOP_Summary_Distribution",
          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk3", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk2", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk1", 'description': top + rpclink }],

          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk-3", 'description': top + rpclink},
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk-2", 'description': top + rpclink},
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Distribution_Disk-1", 'description': top + rpclink}]
          )

rpclayout(dqmitems, "07-EndCap_TOP_Summary",
          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk3", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk2", 'description': top + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk1", 'description': top + rpclink }],

          [{ 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk-3", 'description': top + rpclink},
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk-2", 'description': top + rpclink},
           { 'path': "RPC/Noise/SummaryHistograms/RPCChamberQuality_Ring_vs_Segment_Disk-1", 'description': top + rpclink}]
          )

##------------------------

#Occupancy

rpclayout(dqmitems, "08-Barrel_Occupancy",
          [{ 'path': "RPC/Noise/SummaryHistograms/Occupancy_for_Barrel", 'description': occupancy + rpclink }]
          )

rpclayout(dqmitems, "09-Endcap_Occupancy",
          [{ 'path': "RPC/Noise/SummaryHistograms/Occupancy_for_Endcap", 'description': occupancy + rpclink }]
          )

rpclayout(dqmitems, "10-Barrel_1DOccupancy",
          [{ 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Wheel_2", 'description': occupancy + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Wheel_1", 'description': occupancy + rpclink  }],

          [{ 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Wheel_0", 'description': occupancy + rpclink  },
           { 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Wheel_-1", 'description': occupancy + rpclink  },
           { 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Wheel_-2", 'description': occupancy + rpclink  }]
          )

rpclayout(dqmitems, "11-EndCap_1DOccupancy",
          [{ 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Ring_2", 'description': occupancy + rpclink },
           { 'path': "RPC/Noise/SummaryHistograms/1DOccupancy_Ring_3", 'description': occupancy + rpclink }]
          )

##------------------------

##Number Digi
rpclayout(dqmitems, "12-Barrel_Multiplicity",
          [{ 'path': "RPC/Noise/SummaryHistograms/Multiplicity_Barrel", 'description': nrofdigi + rpclink }])

rpclayout(dqmitems, "13-Endcap_Multiplicity",
          [ { 'path': "RPC/Noise/SummaryHistograms/Multiplicity_Endcap-", 'description': nrofdigi + rpclink },
            { 'path': "RPC/Noise/SummaryHistograms/Multiplicity_Endcap+", 'description': nrofdigi + rpclink  }]
          )
##-----------------------

##Number Cluster

rpclayout(dqmitems, "14-Barrel_Number_Of_Clusters",
          [{ 'path': "RPC/Muon/SummaryHistograms/NumberOfClusters_Barrel", 'description': nrofcl + rpclink }]
          )

rpclayout(dqmitems, "15-Endcap_Number_Of_Clusters",
          [ { 'path': "RPC/Muon/SummaryHistograms/NumberOfClusters_Endcap-", 'description': nrofcl + rpclink },
            { 'path': "RPC/Muon/SummaryHistograms/NumberOfClusters_Endcap+", 'description': nrofcl + rpclink  }]
          )
##-----------------------

##Cluster Size
rpclayout(dqmitems, "16-Barrel_Cluster_Size",
          [{ 'path': "RPC/Muon/SummaryHistograms/ClusterSize_Barrel", 'description': clsize + rpclink }]
          )

rpclayout(dqmitems, "17-Endcap_Cluster_Size",
          [ { 'path': "RPC/Muon/SummaryHistograms/ClusterSize_Endcap-", 'description':  clsize + rpclink },
            { 'path': "RPC/Muon/SummaryHistograms/ClusterSize_Endcap+", 'description':  clsize + rpclink  }]
          )

##-----------------------

##BX
rpclayout(dqmitems, "18-Barrel_Bunch_Crossing",
          [{ 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Wheel_2", 'description': bx + rpclink },
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Wheel_1", 'description': bx + rpclink  }],

          [{ 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Wheel_0", 'description': bx + rpclink  },
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Wheel_-1", 'description': bx + rpclink  },
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Wheel_-2", 'description': bx + rpclink  }]
          )

rpclayout(dqmitems, "19-EndCap_Bunch_Crossing",
          [{ 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_3", 'description': bx + rpclink },
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_2", 'description': bx + rpclink },
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_1", 'description': bx + rpclink }],

          [{ 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_-3", 'description': bx + rpclink},
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_-2", 'description': bx + rpclink},
           { 'path': "RPC/Muon/SummaryHistograms/BxDistribution_Disk_-1", 'description': bx  + rpclink}]
          )
##------------------------

############# number 20 is missing ######### Comming soon!

        ##Efficiency

rpclayout(dqmitems, "21-Statistics",
          [{ 'path': "RPC/RPCEfficiency/Statistics", 'description': eff + rpclink }])

rpclayout(dqmitems, "22-Barrel_Efficiency_Distribution",
          [{ 'path': "RPC/RPCEfficiency/EffBarrelRoll", 'description': eff + rpclink }]
          )

rpclayout(dqmitems, "23-Barrel_Efficiency",
          [{ 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Sector_Wheel_-2", 'description': eff + rpclink },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Sector_Wheel_-1", 'description': eff + rpclink  }],

          [{ 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Sector_Wheel_0", 'description': eff + rpclink  },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Sector_Wheel_+1", 'description': eff + rpclink  },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Sector_Wheel_+2", 'description': eff + rpclink  }]
          )

rpclayout(dqmitems, "24-Endcap_Positive_Efficiency_Distribution",
          [{ 'path': "RPC/RPCEfficiency/EffEndcapPlusRoll", 'description': eff + rpclink }]
          )

rpclayout(dqmitems, "25-Endcap_Negative_Efficiency_Distribution",
          [{ 'path': "RPC/RPCEfficiency/EffEndcapMinusRoll", 'description': eff + rpclink }]
          )

rpclayout(dqmitems, "26-EndCap_Efficiency",
          [{ 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_-3", 'description': eff + rpclink },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_-2", 'description': eff + rpclink },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_-1", 'description': eff + rpclink }],

          [{ 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_1", 'description': eff + rpclink },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_2", 'description': eff + rpclink },
           { 'path': "RPC/RPCEfficiency/Efficiency_Roll_vs_Segment_Disk_3", 'description': eff + rpclink }],
          )
        ##-------------------------
