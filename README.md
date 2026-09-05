# Honor Tools

A collection of tools for exploring Honor devices (particularly VER-N49 - Honor Magic V2), but could
be useful for anyone who have honor device.

XDA-Developers forum: https://xdaforums.com/t/unlock-bootloader-code-for-honor-magic-v2-root-with-magisk.4663415/post-89499716

## HonorSuite patcher

Scripts to override HonorSuite binaries to allow mitmproxy to intercept the requests and see what
kind of url's & parameters it's using. You will also need [MITMProxy](https://mitmproxy.org/) and
[Proxifier](https://www.proxifier.com/) to properly redirect the HonorSuite requests.

How to setup interceptor: https://xdaforums.com/t/op11-edl-downloadtool-to-restore-your-device-to-oxygenos-coloros.4607995/

Also please check the scripts headers in the directory to get a clue how to use them. The produced
patched files are not replacing HonorSuite files to make it happy with checksums.

## Crawler for update.hihonorcdn.com

Allows to get all the xml files from update.hihonorcdn.com and find versions of update zip files to
simplify your search of new update for your honor phone.

## honor_ouc_check.py

Script allows to get the next update hops for your device model directly from Honor Cloud. The only
issue is that it needs your extracted PKI from oeminfo of the device, which is not that easy to do.

I got my PKI via zygote-injection available on 8.0.0.105 - setting com.hihonor.ouc as a target you
can communicate by `com.hihonor.android.os.ProtectAreaEx.readProtectArea` and dump the data from
oeminfo.

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
