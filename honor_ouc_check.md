# Honor OUC Check

So far works on Honor Magic V2, V5 still needs adjustments

Example output:
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
