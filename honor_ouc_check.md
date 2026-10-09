# Honor OUC Check

So far works on Honor Magic V2 and V5

Example output V2:
```
$ python3 tools/honor_ouc_check.py --from-adb --key-attestation ./pki/key_attestation.txt --device-certificate ./pki/device_certificate.txt --walk
{
  "device": {
    "model": "VER-N49",
    "cust": "C636",
    "vendorCountry": "def_spcseas",
    "deviceId": "A2VQ024102001574",
    "base": "VER-LGRP2-OVS 8.0.0.105",
    "custPkg": "VER-N49-CUST 8.0.0.2(C636)",
    "preloadPkg": "VER-N49-PRELOAD 8.0.0.2(C636R2)"
  },
  "hops": [
    {
      "status": 0,
      "blVersionType": 1,
      "current": "VER-N49 8.0.0.105(C636E2R2P2)",
      "target": "VER-N49 8.0.0.142(C636E2R2P2)",
      "lane": "HotaLane_VER-N49_def_spcseas_C636_R2",
      "updateAction": "upgrade",
      "descriptPackageId": "474467",
      "components": [
        {
          "displayVersionNumber": "VER-LGRP2-OVS 8.0.0.142",
          "versionNumber": "VER-LGRP2-OVS 8.0.0.142",
          "versionPackageType": 2
        },
        {
          "displayVersionNumber": "VER-N49-CUST 8.0.0.2(C636)",
          "versionNumber": "VER-N49-CUST 8.0.0.2(C636)",
          "versionPackageType": 3
        },
        {
          "displayVersionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)",
          "versionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)",
          "versionPackageType": 4
        }
      ],
      "updatePackages": [
        {
          "packageIndex": 1,
          "versionId": "474462",
          "versionPackageType": 2
        },
        {
          "packageIndex": 2,
          "versionId": "335329",
          "versionPackageType": 3
        },
        {
          "packageIndex": 3,
          "versionId": "335330",
          "versionPackageType": 4
        }
      ]
    },
    {
      "status": 1,
      "blVersionType": 3,
      "current": "VER-LGRP2-OVS 8.0.0.142",
      "target": null,
      "lane": "PatchLane_VER-LGRP2-OVS",
      "updateAction": "upgrade",
      "descriptPackageId": null,
      "components": [],
      "updatePackages": []
    }
  ],
  "packages": [
    {
      "versionId": "474462",
      "versionNumber": "VER-LGRP2-OVS 8.0.0.142",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v474462/f1/"
    },
    {
      "versionId": "335329",
      "versionNumber": "VER-N49-CUST 8.0.0.2(C636)",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v335329/f1/"
    },
    {
      "versionId": "335330",
      "versionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v335330/f1/"
    },
    {
      "versionId": "474467",
      "versionNumber": "253810832",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v474467/f1/"
    }
  ],
  "filelists": [],
  "checkHttp": 200,
  "check": {
    "result": {
      "blVersionCheckResults": [
        {
          "blVersionInfo": {
            "blVersionType": 1,
            "currentBlVersionId": "7186974782800654016",
            "currentBlVersionNumber": "VER-N49 8.0.0.105(C636E2R2P2)",
            "laneId": "7128363529207672512",
            "laneName": "HotaLane_VER-N49_def_spcseas_C636_R2",
            "targetBlVersionId": "7262402987195494080",
            "targetBlVersionNumber": "VER-N49 8.0.0.142(C636E2R2P2)",
            "targetCowCompressControl": 2,
            "updateAction": "upgrade"
          },
          "blVersionType": 1,
          "currentVersionMatchType": 1,
          "descriptPackageId": "474467",
          "dynamicAttr": {
            "softwarePlatMSVersion": "8.0"
          },
          "mccId": 0,
          "pollingPeriod": "10080",
          "releaseRuleAttr": "",
          "ruleGroupId": "7432697439435747008",
          "status": 0,
          "targetBlComponents": [
            {
              "displayVersionNumber": "VER-LGRP2-OVS 8.0.0.142",
              "versionNumber": "VER-LGRP2-OVS 8.0.0.142",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "VER-N49-CUST 8.0.0.2(C636)",
              "versionNumber": "VER-N49-CUST 8.0.0.2(C636)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)",
              "versionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "474462",
              "versionPackageType": 2
            },
            {
              "packageIndex": 2,
              "versionId": "335329",
              "versionPackageType": 3
            },
            {
              "packageIndex": 3,
              "versionId": "335330",
              "versionPackageType": 4
            }
          ],
          "updatePathAttr": "patchVersion=null",
          "upgradePathId": "7432697439389609664",
          "userType": "2"
        },
        {
          "blVersionInfo": {
            "blVersionType": 3,
            "currentBlVersionId": 1,
            "currentBlVersionNumber": "VER-LGRP2-OVS 8.0.0.142",
            "laneId": "7150816926905003712",
            "laneName": "PatchLane_VER-LGRP2-OVS",
            "targetBlVersionId": 0,
            "updateAction": "upgrade"
          },
          "blVersionType": 3,
          "currentVersionMatchType": 0,
          "mccId": 0,
          "pollingPeriod": "10080",
          "ruleGroupId": 0,
          "status": 1,
          "upgradePathId": 0,
          "userType": "2"
        }
      ],
      "checkResult": 0,
      "cotaInfo": {
        "country": "HK",
        "vendorCota": "DEFAULT",
        "vendorExpiredTime": 1788561290346
      },
      "versionList": [
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v474462/f1/",
          "versionId": "474462",
          "versionNumber": "VER-LGRP2-OVS 8.0.0.142"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v335329/f1/",
          "versionId": "335329",
          "versionNumber": "VER-N49-CUST 8.0.0.2(C636)"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v335330/f1/",
          "versionId": "335330",
          "versionNumber": "VER-N49-PRELOAD 8.0.0.2(C636R2)"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v474467/f1/",
          "versionId": "474467",
          "versionNumber": "253810832"
        }
      ]
    },
    "status": 0
  },
  "walk": [
    {
      "from": "8.0.0.142",
      "http": 200,
      "hops": [
        {
          "status": 0,
          "blVersionType": 1,
          "current": "VER-N49 8.0.0.142(C636E2R2P2)",
          "target": "VER-N49 9.0.0.131(C636E4R2P2)",
          "lane": "HotaLane_VER-N49_def_spcseas_C636_R2",
          "updateAction": "upgrade",
          "descriptPackageId": "488695",
          "components": [
            {
              "displayVersionNumber": "VER-LGRP2-OVS 9.0.0.131",
              "versionNumber": "VER-LGRP2-OVS 9.0.0.131",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "VER-N49-CUST 9.0.0.4(C636)",
              "versionNumber": "VER-N49-CUST 9.0.0.4(C636)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "VER-N49-PRELOAD 9.0.0.2(C636R2)",
              "versionNumber": "VER-N49-PRELOAD 9.0.0.2(C636R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "488688",
              "versionPackageType": 2
            },
            {
              "packageIndex": 2,
              "versionId": "488689",
              "versionPackageType": 3
            },
            {
              "packageIndex": 3,
              "versionId": "458168",
              "versionPackageType": 4
            }
          ]
        },
        {
          "status": 0,
          "blVersionType": 3,
          "current": "VER-LGRP2-OVS 9.0.0.131",
          "target": "VER-LGRP2-OVS 9.0.0.131(patch03)",
          "lane": "PatchLane_VER-LGRP2-OVS",
          "updateAction": "upgrade",
          "descriptPackageId": "494074",
          "components": [
            {
              "displayVersionNumber": "VER-LGRP2-OVS 9.0.0.131",
              "versionNumber": "VER-LGRP2-OVS 9.0.0.131",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "patch03",
              "versionNumber": "patch03",
              "versionPackageType": 13
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "494073",
              "versionPackageType": 13
            }
          ]
        }
      ],
      "check": {
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionInfo": {
                "blVersionType": 1,
                "currentBlVersionId": "7262402987195494080",
                "currentBlVersionNumber": "VER-N49 8.0.0.142(C636E2R2P2)",
                "laneId": "7128363529207672512",
                "laneName": "HotaLane_VER-N49_def_spcseas_C636_R2",
                "targetBlVersionId": "7269916725528096448",
                "targetBlVersionNumber": "VER-N49 9.0.0.131(C636E4R2P2)",
                "targetCowCompressControl": 2,
                "updateAction": "upgrade"
              },
              "blVersionType": 1,
              "currentVersionMatchType": 1,
              "descriptPackageId": "488695",
              "dynamicAttr": {
                "softwarePlatMSVersion": "9.0"
              },
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "romSurveyOn",
              "ruleGroupId": "7278007270972452544",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "VER-LGRP2-OVS 9.0.0.131",
                  "versionNumber": "VER-LGRP2-OVS 9.0.0.131",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "VER-N49-CUST 9.0.0.4(C636)",
                  "versionNumber": "VER-N49-CUST 9.0.0.4(C636)",
                  "versionPackageType": 3
                },
                {
                  "displayVersionNumber": "VER-N49-PRELOAD 9.0.0.2(C636R2)",
                  "versionNumber": "VER-N49-PRELOAD 9.0.0.2(C636R2)",
                  "versionPackageType": 4
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "488688",
                  "versionPackageType": 2
                },
                {
                  "packageIndex": 2,
                  "versionId": "488689",
                  "versionPackageType": 3
                },
                {
                  "packageIndex": 3,
                  "versionId": "458168",
                  "versionPackageType": 4
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7278007270934703808",
              "userType": "2"
            },
            {
              "blVersionInfo": {
                "blVersionType": 3,
                "currentBlVersionId": 1,
                "currentBlVersionNumber": "VER-LGRP2-OVS 9.0.0.131",
                "laneId": "7150816926905003712",
                "laneName": "PatchLane_VER-LGRP2-OVS",
                "targetBlVersionId": "7275800303403134656",
                "targetBlVersionNumber": "VER-LGRP2-OVS 9.0.0.131(patch03)",
                "updateAction": "upgrade"
              },
              "blVersionType": 3,
              "currentVersionMatchType": 0,
              "descriptPackageId": "494074",
              "dynamicAttr": {},
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "",
              "ruleGroupId": "7282690870028398285",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "VER-LGRP2-OVS 9.0.0.131",
                  "versionNumber": "VER-LGRP2-OVS 9.0.0.131",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "patch03",
                  "versionNumber": "patch03",
                  "versionPackageType": 13
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "494073",
                  "versionPackageType": 13
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7282690869999038144",
              "userType": "2"
            }
          ],
          "checkResult": 0,
          "cotaInfo": {
            "country": "HK",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1788561292907
          },
          "versionList": [
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v488688/f1/",
              "versionId": "488688",
              "versionNumber": "VER-LGRP2-OVS 9.0.0.131"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v488689/f1/",
              "versionId": "488689",
              "versionNumber": "VER-N49-CUST 9.0.0.4(C636)"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v458168/f1/",
              "versionId": "458168",
              "versionNumber": "VER-N49-PRELOAD 9.0.0.2(C636R2)"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v488695/f1/",
              "versionId": "488695",
              "versionNumber": "253855334"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v494073/f1/",
              "versionId": "494073",
              "versionNumber": "patch03"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v494074/f1/",
              "versionId": "494074",
              "versionNumber": "253888770"
            }
          ]
        },
        "status": 0
      }
    }
  ]
}
```

Example output V5:
```
python3 ./honor_ouc_check.py --from-adb --walk --filelist --key-attestation pki_honor_magic_v5/key_attestation.txt --device-certificate pki_honor_magic_v5/device_certificate.txt
{
  "device": {
    "model": "MBH-N49",
    "cust": "C431",
    "vendorCountry": "def_eea",
    "boardID": "8119",
    "deviceId": "AWRT026122000810",
    "fingerprint": "HONOR/MBH-N49EEA/HNMBHX:15/HONORMBH-N49/9.0.1.160C431E3R2P2:user/release-keys",
    "clientVersion": "160148100",
    "base": "MBH-LGRP2-OVS 9.0.1.160",
    "custPkg": "MBH-N49-CUST 9.0.1.3(C431)",
    "preloadPkg": "MBH-N49-PRELOAD 9.0.1.2(C431R2)"
  },
  "hops": [
    {
      "status": 0,
      "blVersionType": 1,
      "current": "MBH-N49 9.0.1.160(C431E3R2P2)",
      "target": "MBH-N49 10.0.0.122(C431E3R2P2)",
      "lane": "HotaLane_MBH-N49_def_eea_C431_R2",
      "updateAction": "upgrade",
      "descriptPackageId": "692667",
      "components": [
        {
          "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.122",
          "versionNumber": "MBH-LGRP2-OVS 10.0.0.122",
          "versionPackageType": 2
        },
        {
          "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
          "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
          "versionPackageType": 3
        },
        {
          "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
          "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
          "versionPackageType": 4
        }
      ],
      "updatePackages": [
        {
          "packageIndex": 1,
          "versionId": "692661",
          "versionPackageType": 2
        },
        {
          "packageIndex": 2,
          "versionId": "692662",
          "versionPackageType": 3
        },
        {
          "packageIndex": 3,
          "versionId": "667758",
          "versionPackageType": 4
        }
      ]
    },
    {
      "status": 0,
      "blVersionType": 3,
      "current": "MBH-LGRP2-OVS 10.0.0.122",
      "target": "MBH-LGRP2-OVS 10.0.0.122(patch01)",
      "lane": "PatchLane_MBH-LGRP2-OVS",
      "updateAction": "upgrade",
      "descriptPackageId": "699561",
      "components": [
        {
          "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.122",
          "versionNumber": "MBH-LGRP2-OVS 10.0.0.122",
          "versionPackageType": 2
        },
        {
          "displayVersionNumber": "patch01",
          "versionNumber": "patch01",
          "versionPackageType": 13
        }
      ],
      "updatePackages": [
        {
          "packageIndex": 1,
          "versionId": "699560",
          "versionPackageType": 13
        }
      ]
    }
  ],
  "packages": [
    {
      "versionId": "692661",
      "versionNumber": "MBH-LGRP2-OVS 10.0.0.122",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692661/f1/"
    },
    {
      "versionId": "692662",
      "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692662/f1/"
    },
    {
      "versionId": "667758",
      "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v667758/f1/"
    },
    {
      "versionId": "692667",
      "versionNumber": "254532190",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692667/f1/"
    },
    {
      "versionId": "699560",
      "versionNumber": "patch01",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v699560/f1/"
    },
    {
      "versionId": "699561",
      "versionNumber": "254566250",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v699561/f1/"
    }
  ],
  "filelists": [
    {
      "versionId": "692661",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692661/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "base",
      "supportPKI": "1",
      "vendorPackage": "update_base.zip",
      "vendorName": "base",
      "files": [
        {
          "name": "update_base.zip",
          "size": 2380741270,
          "sha256": "B6BC1A4132F7940B3DFC1683E16308E0E15FFC62073B0860DB3F34F325A8483D",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v692661/f1/full/update_base.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "10677661696",
        "fileSize": "2380733564"
      }
    },
    {
      "versionId": "692662",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692662/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "cust",
      "supportPKI": "1",
      "vendorPackage": "update_cust_MBH-N49_def_eea.zip",
      "vendorName": "cust",
      "files": [
        {
          "name": "update_cust_MBH-N49_def_eea.zip",
          "size": 15786,
          "sha256": "F6F365D82B74825EE0C7012F1D12B94FCFA6F2933B3E5BA8084A2FF423AC84FF",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v692662/f1/full/update_cust_MBH-N49_def_eea.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "726298624",
        "fileSize": "8493"
      }
    },
    {
      "versionId": "667758",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v667758/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "preload",
      "supportPKI": "1",
      "vendorPackage": "update_preload_MBH-N49_def_eea_R2.zip",
      "vendorName": "preload",
      "files": [
        {
          "name": "update_preload_MBH-N49_def_eea_R2.zip",
          "size": 124227,
          "sha256": "5242E339E63E94F1AE42DD1DFBE06A6A2693061D8FA982900C88027B68F0F642",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v667758/f1/full/update_preload_MBH-N49_def_eea_R2.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "2166353920",
        "fileSize": "116906"
      }
    },
    {
      "versionId": "699560",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v699560/f1/full/filelist.xml",
      "http": 200,
      "packageType": "",
      "packageSolution": "",
      "supportPKI": "",
      "vendorPackage": "update.zip",
      "vendorName": "common",
      "files": [
        {
          "name": "changelog.xml",
          "size": 579,
          "sha256": "15B4ACEC49C6BDB9769828035278F9C88C7089550BD6FFB6A83DFE723D6DB767",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v699560/f1/full/changelog.xml"
        },
        {
          "name": "update.zip",
          "size": 4034712,
          "sha256": "3DC7A0EC2BB25AA95C90FAE5995D0F939D815E39B0F21C7FC38A8A25E5709EDD",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v699560/f1/full/update.zip"
        }
      ],
      "virtualAb": {
        "cowsize": null,
        "fileSize": null
      }
    },
    {
      "versionId": "760952",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v760952/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "base",
      "supportPKI": "1",
      "vendorPackage": "update_base.zip",
      "vendorName": "base",
      "files": [
        {
          "name": "update_base.zip",
          "size": 744329609,
          "sha256": "B55659F21E8911175A60A83E73241D450FD6D96A03A11CA45C895199FE444012",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v760952/f1/full/update_base.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "9569177600",
        "fileSize": "744321914"
      }
    },
    {
      "versionId": "824211",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v824211/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "base",
      "supportPKI": "1",
      "vendorPackage": "update_base.zip",
      "vendorName": "base",
      "files": [
        {
          "name": "update_base.zip",
          "size": 186164078,
          "sha256": "578350409B34123FAA99707FE7333998CC6A8A3535614DF6159529F8F7370801",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v824211/f1/full/update_base.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "4127768576",
        "fileSize": "186156382"
      }
    },
    {
      "versionId": "889733",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v889733/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "base",
      "supportPKI": "1",
      "vendorPackage": "update_base.zip",
      "vendorName": "base",
      "files": [
        {
          "name": "update_base.zip",
          "size": 1906540058,
          "sha256": "220CD11BAFB3B48489C029C09EE05977D73125F551DD8B54114A2BA98CB1868A",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v889733/f1/full/update_base.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "11653926912",
        "fileSize": "1906532351"
      }
    },
    {
      "versionId": "844131",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v844131/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "cust",
      "supportPKI": "1",
      "vendorPackage": "update_cust_MBH-N49_def_eea.zip",
      "vendorName": "cust",
      "files": [
        {
          "name": "update_cust_MBH-N49_def_eea.zip",
          "size": 15579,
          "sha256": "E5474AD52826546DBA03CA42EF9A2B5120076BA889F7CA40BC7FAA91780CA881",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v844131/f1/full/update_cust_MBH-N49_def_eea.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "726298624",
        "fileSize": "8285"
      }
    },
    {
      "versionId": "913757",
      "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v913757/f1/full/filelist.xml",
      "http": 200,
      "packageType": "increment",
      "packageSolution": "base",
      "supportPKI": "1",
      "vendorPackage": "update_base.zip",
      "vendorName": "base",
      "files": [
        {
          "name": "update_base.zip",
          "size": 181374239,
          "sha256": "2FCE87EA595C0F1700018B05A7947F6A0F155F5FEF157F4E705B550554A539A2",
          "download": "http://update.hihonorcdn.com/TDS/data/bl/files/v913757/f1/full/update_base.zip"
        }
      ],
      "virtualAb": {
        "cowsize": "4068139008",
        "fileSize": "181366545"
      }
    }
  ],
  "checkHttp": 200,
  "check": {
    "result": {
      "blVersionCheckResults": [
        {
          "blVersionInfo": {
            "blVersionType": 1,
            "currentBlVersionId": "7383387900857413312",
            "currentBlVersionNumber": "MBH-N49 9.0.1.160(C431E3R2P2)",
            "laneId": "7322830157277163200",
            "laneName": "HotaLane_MBH-N49_def_eea_C431_R2",
            "targetBlVersionId": "7393829423960944320",
            "targetBlVersionNumber": "MBH-N49 10.0.0.122(C431E3R2P2)",
            "targetCowCompressControl": 0,
            "updateAction": "upgrade"
          },
          "blVersionType": 1,
          "currentVersionMatchType": 1,
          "descriptPackageId": "692667",
          "dynamicAttr": {
            "softwarePlatMSVersion": "10.0"
          },
          "mccId": 0,
          "pollingPeriod": "10080",
          "releaseRuleAttr": "romSurveyOn",
          "ruleGroupId": "7498300476111580884",
          "status": 0,
          "targetBlComponents": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.122",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.122",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "692661",
              "versionPackageType": 2
            },
            {
              "packageIndex": 2,
              "versionId": "692662",
              "versionPackageType": 3
            },
            {
              "packageIndex": 3,
              "versionId": "667758",
              "versionPackageType": 4
            }
          ],
          "updatePathAttr": "patchVersion=null",
          "upgradePathId": "7498300476069637832",
          "userType": "2"
        },
        {
          "blVersionInfo": {
            "blVersionType": 3,
            "currentBlVersionId": 1,
            "currentBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.122",
            "laneId": "7353599984782405312",
            "laneName": "PatchLane_MBH-LGRP2-OVS",
            "targetBlVersionId": "7398984292631965376",
            "targetBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.122(patch01)",
            "updateAction": "upgrade"
          },
          "blVersionType": 3,
          "currentVersionMatchType": 0,
          "descriptPackageId": "699561",
          "dynamicAttr": {},
          "mccId": 0,
          "pollingPeriod": "10080",
          "releaseRuleAttr": "",
          "ruleGroupId": "7417851890677182174",
          "status": 0,
          "targetBlComponents": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.122",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.122",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "patch01",
              "versionNumber": "patch01",
              "versionPackageType": 13
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "699560",
              "versionPackageType": 13
            }
          ],
          "updatePathAttr": "patchVersion=null",
          "upgradePathId": "7417851890647822016",
          "userType": "2"
        }
      ],
      "checkResult": 0,
      "cotaInfo": {
        "country": "AD",
        "vendorCota": "DEFAULT",
        "vendorExpiredTime": 1792172399275
      },
      "versionList": [
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692661/f1/",
          "versionId": "692661",
          "versionNumber": "MBH-LGRP2-OVS 10.0.0.122"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692662/f1/",
          "versionId": "692662",
          "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v667758/f1/",
          "versionId": "667758",
          "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v692667/f1/",
          "versionId": "692667",
          "versionNumber": "254532190"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v699560/f1/",
          "versionId": "699560",
          "versionNumber": "patch01"
        },
        {
          "reserveUrl": "update.hihonorcdn.com",
          "storageType": 0,
          "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v699561/f1/",
          "versionId": "699561",
          "versionNumber": "254566250"
        }
      ]
    },
    "status": 0
  },
  "walk": [
    {
      "from": {
        "base": "MBH-LGRP2-OVS 10.0.0.122",
        "cust": "MBH-N49-CUST 10.0.0.3(C431)",
        "preload": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
        "patch": "patch00"
      },
      "http": 200,
      "errCode": null,
      "hops": [
        {
          "status": 0,
          "blVersionType": 1,
          "current": "MBH-N49 10.0.0.122(C431E3R2P2)",
          "target": "MBH-N49 10.0.0.135(C431E3R2P2)",
          "lane": "HotaLane_MBH-N49_def_eea_C431_R2",
          "updateAction": "upgrade",
          "descriptPackageId": "760957",
          "components": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.135",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.135",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "760952",
              "versionPackageType": 2
            }
          ]
        },
        {
          "status": 1,
          "blVersionType": 3,
          "current": "MBH-LGRP2-OVS 10.0.0.135",
          "target": null,
          "lane": "PatchLane_MBH-LGRP2-OVS",
          "updateAction": "upgrade",
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        }
      ],
      "check": {
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionInfo": {
                "blVersionType": 1,
                "currentBlVersionId": "7393829423960944320",
                "currentBlVersionNumber": "MBH-N49 10.0.0.122(C431E3R2P2)",
                "laneId": "7322830157277163200",
                "laneName": "HotaLane_MBH-N49_def_eea_C431_R2",
                "targetBlVersionId": "7425466521155399360",
                "targetBlVersionNumber": "MBH-N49 10.0.0.135(C431E3R2P2)",
                "targetCowCompressControl": 2,
                "updateAction": "upgrade"
              },
              "blVersionType": 1,
              "currentVersionMatchType": 1,
              "descriptPackageId": "760957",
              "dynamicAttr": {
                "softwarePlatMSVersion": "10.0"
              },
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "preloadAppCheck=0",
              "ruleGroupId": "7498300468951903948",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.135",
                  "versionNumber": "MBH-LGRP2-OVS 10.0.0.135",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
                  "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
                  "versionPackageType": 3
                },
                {
                  "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionPackageType": 4
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "760952",
                  "versionPackageType": 2
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7498300468914155200",
              "userType": "2"
            },
            {
              "blVersionInfo": {
                "blVersionType": 3,
                "currentBlVersionId": 1,
                "currentBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.135",
                "laneId": "7353599984782405312",
                "laneName": "PatchLane_MBH-LGRP2-OVS",
                "targetBlVersionId": 0,
                "updateAction": "upgrade"
              },
              "blVersionType": 3,
              "currentVersionMatchType": 0,
              "mccId": 0,
              "pollingPeriod": "10080",
              "ruleGroupId": 0,
              "status": 1,
              "upgradePathId": 0,
              "userType": "2"
            }
          ],
          "checkResult": 0,
          "cotaInfo": {
            "country": "AD",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1792172405141
          },
          "versionList": [
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v760952/f1/",
              "versionId": "760952",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.135"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v760957/f1/",
              "versionId": "760957",
              "versionNumber": "254778752"
            }
          ]
        },
        "status": 0
      }
    },
    {
      "from": {
        "base": "MBH-LGRP2-OVS 10.0.0.135",
        "cust": "MBH-N49-CUST 10.0.0.3(C431)",
        "preload": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
        "patch": "patch00"
      },
      "http": 200,
      "errCode": null,
      "hops": [
        {
          "status": 0,
          "blVersionType": 1,
          "current": "MBH-N49 10.0.0.135(C431E3R2P2)",
          "target": "MBH-N49 10.0.0.154(C431E3R2P2)",
          "lane": "HotaLane_MBH-N49_def_eea_C431_R2",
          "updateAction": "upgrade",
          "descriptPackageId": "824215",
          "components": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.154",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.154",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "824211",
              "versionPackageType": 2
            }
          ]
        },
        {
          "status": 1,
          "blVersionType": 3,
          "current": "MBH-LGRP2-OVS 10.0.0.154",
          "target": null,
          "lane": "PatchLane_MBH-LGRP2-OVS",
          "updateAction": "upgrade",
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        }
      ],
      "check": {
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionInfo": {
                "blVersionType": 1,
                "currentBlVersionId": "7425466521155399360",
                "currentBlVersionNumber": "MBH-N49 10.0.0.135(C431E3R2P2)",
                "laneId": "7322830157277163200",
                "laneName": "HotaLane_MBH-N49_def_eea_C431_R2",
                "targetBlVersionId": "7463145087011516096",
                "targetBlVersionNumber": "MBH-N49 10.0.0.154(C431E3R2P2)",
                "targetCowCompressControl": 2,
                "updateAction": "upgrade"
              },
              "blVersionType": 1,
              "currentVersionMatchType": 1,
              "descriptPackageId": "824215",
              "dynamicAttr": {
                "softwarePlatMSVersion": "10.0"
              },
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "",
              "ruleGroupId": "7500159883241975496",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.154",
                  "versionNumber": "MBH-LGRP2-OVS 10.0.0.154",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
                  "versionNumber": "MBH-N49-CUST 10.0.0.3(C431)",
                  "versionPackageType": 3
                },
                {
                  "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionPackageType": 4
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "824211",
                  "versionPackageType": 2
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7500159883204226752",
              "userType": "2"
            },
            {
              "blVersionInfo": {
                "blVersionType": 3,
                "currentBlVersionId": 1,
                "currentBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.154",
                "laneId": "7353599984782405312",
                "laneName": "PatchLane_MBH-LGRP2-OVS",
                "targetBlVersionId": 0,
                "updateAction": "upgrade"
              },
              "blVersionType": 3,
              "currentVersionMatchType": 0,
              "mccId": 0,
              "pollingPeriod": "10080",
              "ruleGroupId": 0,
              "status": 1,
              "upgradePathId": 0,
              "userType": "2"
            }
          ],
          "checkResult": 0,
          "cotaInfo": {
            "country": "AD",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1792172406729
          },
          "versionList": [
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v824211/f1/",
              "versionId": "824211",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.154"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v824215/f1/",
              "versionId": "824215",
              "versionNumber": "255052602"
            }
          ]
        },
        "status": 0
      }
    },
    {
      "from": {
        "base": "MBH-LGRP2-OVS 10.0.0.154",
        "cust": "MBH-N49-CUST 10.0.0.3(C431)",
        "preload": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
        "patch": "patch00"
      },
      "http": 200,
      "errCode": null,
      "hops": [
        {
          "status": 0,
          "blVersionType": 1,
          "current": "MBH-N49 10.0.0.154(C431E3R2P2)",
          "target": "MBH-N49 10.0.0.165(C431E5R2P2)",
          "lane": "HotaLane_MBH-N49_def_eea_C431_R2",
          "updateAction": "upgrade",
          "descriptPackageId": "889744",
          "components": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.165",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.165",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
              "versionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "889733",
              "versionPackageType": 2
            },
            {
              "packageIndex": 2,
              "versionId": "844131",
              "versionPackageType": 3
            }
          ]
        },
        {
          "status": 1,
          "blVersionType": 3,
          "current": "MBH-LGRP2-OVS 10.0.0.165",
          "target": null,
          "lane": "PatchLane_MBH-LGRP2-OVS",
          "updateAction": "upgrade",
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        }
      ],
      "check": {
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionInfo": {
                "blVersionType": 1,
                "currentBlVersionId": "7463145087011516096",
                "currentBlVersionNumber": "MBH-N49 10.0.0.154(C431E3R2P2)",
                "laneId": "7322830157277163200",
                "laneName": "HotaLane_MBH-N49_def_eea_C431_R2",
                "targetBlVersionId": "7488163173426917056",
                "targetBlVersionNumber": "MBH-N49 10.0.0.165(C431E5R2P2)",
                "targetCowCompressControl": 2,
                "updateAction": "upgrade"
              },
              "blVersionType": 1,
              "currentVersionMatchType": 1,
              "descriptPackageId": "889744",
              "dynamicAttr": {
                "softwarePlatMSVersion": "10.0"
              },
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "",
              "ruleGroupId": "7498300454020181700",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.165",
                  "versionNumber": "MBH-LGRP2-OVS 10.0.0.165",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
                  "versionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
                  "versionPackageType": 3
                },
                {
                  "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionPackageType": 4
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "889733",
                  "versionPackageType": 2
                },
                {
                  "packageIndex": 2,
                  "versionId": "844131",
                  "versionPackageType": 3
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7498300453982432963",
              "userType": "2"
            },
            {
              "blVersionInfo": {
                "blVersionType": 3,
                "currentBlVersionId": 1,
                "currentBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.165",
                "laneId": "7353599984782405312",
                "laneName": "PatchLane_MBH-LGRP2-OVS",
                "targetBlVersionId": 0,
                "updateAction": "upgrade"
              },
              "blVersionType": 3,
              "currentVersionMatchType": 0,
              "mccId": 0,
              "pollingPeriod": "10080",
              "ruleGroupId": 0,
              "status": 1,
              "upgradePathId": 0,
              "userType": "2"
            }
          ],
          "checkResult": 0,
          "cotaInfo": {
            "country": "AD",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1792172408077
          },
          "versionList": [
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v889733/f1/",
              "versionId": "889733",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.165"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v844131/f1/",
              "versionId": "844131",
              "versionNumber": "MBH-N49-CUST 10.0.0.5(C431)"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v889744/f1/",
              "versionId": "889744",
              "versionNumber": "255270836"
            }
          ]
        },
        "status": 0
      }
    },
    {
      "from": {
        "base": "MBH-LGRP2-OVS 10.0.0.165",
        "cust": "MBH-N49-CUST 10.0.0.5(C431)",
        "preload": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
        "patch": "patch00"
      },
      "http": 200,
      "errCode": null,
      "hops": [
        {
          "status": 0,
          "blVersionType": 1,
          "current": "MBH-N49 10.0.0.165(C431E5R2P2)",
          "target": "MBH-N49 10.0.0.168(C431E5R2P2)",
          "lane": "HotaLane_MBH-N49_def_eea_C431_R2",
          "updateAction": "upgrade",
          "descriptPackageId": "913758",
          "components": [
            {
              "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.168",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.168",
              "versionPackageType": 2
            },
            {
              "displayVersionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
              "versionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
              "versionPackageType": 3
            },
            {
              "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
              "versionPackageType": 4
            }
          ],
          "updatePackages": [
            {
              "packageIndex": 1,
              "versionId": "913757",
              "versionPackageType": 2
            }
          ]
        },
        {
          "status": 1,
          "blVersionType": 3,
          "current": "MBH-LGRP2-OVS 10.0.0.168",
          "target": null,
          "lane": "PatchLane_MBH-LGRP2-OVS",
          "updateAction": "upgrade",
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        }
      ],
      "check": {
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionInfo": {
                "blVersionType": 1,
                "currentBlVersionId": "7488163173426917056",
                "currentBlVersionNumber": "MBH-N49 10.0.0.165(C431E5R2P2)",
                "laneId": "7322830157277163200",
                "laneName": "HotaLane_MBH-N49_def_eea_C431_R2",
                "targetBlVersionId": "7504014366308953792",
                "targetBlVersionNumber": "MBH-N49 10.0.0.168(C431E5R2P2)",
                "targetCowCompressControl": 2,
                "updateAction": "upgrade"
              },
              "blVersionType": 1,
              "currentVersionMatchType": 1,
              "descriptPackageId": "913758",
              "dynamicAttr": {
                "softwarePlatMSVersion": "10.0"
              },
              "mccId": 0,
              "pollingPeriod": "10080",
              "releaseRuleAttr": "",
              "ruleGroupId": "7508478962436533968",
              "status": 0,
              "targetBlComponents": [
                {
                  "displayVersionNumber": "MBH-LGRP2-OVS 10.0.0.168",
                  "versionNumber": "MBH-LGRP2-OVS 10.0.0.168",
                  "versionPackageType": 2
                },
                {
                  "displayVersionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
                  "versionNumber": "MBH-N49-CUST 10.0.0.5(C431)",
                  "versionPackageType": 3
                },
                {
                  "displayVersionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionNumber": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
                  "versionPackageType": 4
                }
              ],
              "updatePackages": [
                {
                  "packageIndex": 1,
                  "versionId": "913757",
                  "versionPackageType": 2
                }
              ],
              "updatePathAttr": "patchVersion=null",
              "upgradePathId": "7508478962394590919",
              "userType": "2"
            },
            {
              "blVersionInfo": {
                "blVersionType": 3,
                "currentBlVersionId": 1,
                "currentBlVersionNumber": "MBH-LGRP2-OVS 10.0.0.168",
                "laneId": "7353599984782405312",
                "laneName": "PatchLane_MBH-LGRP2-OVS",
                "targetBlVersionId": 0,
                "updateAction": "upgrade"
              },
              "blVersionType": 3,
              "currentVersionMatchType": 0,
              "mccId": 0,
              "pollingPeriod": "10080",
              "ruleGroupId": 0,
              "status": 1,
              "upgradePathId": 0,
              "userType": "2"
            }
          ],
          "checkResult": 0,
          "cotaInfo": {
            "country": "AD",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1792172409407
          },
          "versionList": [
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v913757/f1/",
              "versionId": "913757",
              "versionNumber": "MBH-LGRP2-OVS 10.0.0.168"
            },
            {
              "reserveUrl": "update.hihonorcdn.com",
              "storageType": 0,
              "url": "http://update.hihonorcdn.com/TDS/data/bl/files/v913758/f1/",
              "versionId": "913758",
              "versionNumber": "255440354"
            }
          ]
        },
        "status": 0
      }
    },
    {
      "from": {
        "base": "MBH-LGRP2-OVS 10.0.0.168",
        "cust": "MBH-N49-CUST 10.0.0.5(C431)",
        "preload": "MBH-N49-PRELOAD 10.0.0.2(C431R2)",
        "patch": "patch00"
      },
      "http": 200,
      "errCode": "101003404",
      "hops": [
        {
          "status": 1,
          "blVersionType": 1,
          "current": null,
          "target": null,
          "lane": null,
          "updateAction": null,
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        },
        {
          "status": 1,
          "blVersionType": 3,
          "current": null,
          "target": null,
          "lane": null,
          "updateAction": null,
          "descriptPackageId": null,
          "components": [],
          "updatePackages": []
        }
      ],
      "check": {
        "errCode": "101003404",
        "errMsg": "{'Message':'ota packageInfo is not exist', 'ExceptionMessage':'ota packageInfo is not exist'}",
        "result": {
          "blVersionCheckResults": [
            {
              "blVersionType": 1,
              "pollingPeriod": "10080",
              "status": 1
            },
            {
              "blVersionType": 3,
              "status": 1
            }
          ],
          "cotaInfo": {
            "country": "AD",
            "vendorCota": "DEFAULT",
            "vendorExpiredTime": 1792172410073
          }
        },
        "status": 1
      }
    }
  ]
}
```
