# xlr-f5-plugin
Plugin for GTM/LTM

## Preface
This document describes the functionality provide by the `xlr-f5-plugin`.

## CI Status

[![Build Status][xlr-f5-plugin-travis-image] ][xlr-f5-plugin-travis-url]
[![Codacy][xlr-f5-plugin-codacy-image] ][xlr-f5-plugin-codacy-url]
[![Code Climate][xlr-f5-plugin-code-climate-image] ][xlr-f5-plugin-code-climate-url]
[![License: MIT][xlr-f5-plugin-license-image] ][xlr-f5-plugin-license-url]
[![Github All Releases][xlr-f5-plugin-downloads-image] ]()

[xlr-f5-plugin-travis-image]: https://travis-ci.org/xebialabs-community/xlr-f5-plugin.svg?branch=master
[xlr-f5-plugin-travis-url]: https://travis-ci.org/xebialabs-community/xlr-f5-plugin
[xlr-f5-plugin-codacy-image]: https://api.codacy.com/project/badge/Grade/eca7756dec96451f82a87fd09670096a
[xlr-f5-plugin-codacy-url]: https://www.codacy.com/app/gsajwan/xlr-f5-plugin
[xlr-f5-plugin-code-climate-image]: https://codeclimate.com/github/xebialabs-community/xlr-f5-plugin/badges/gpa.svg
[xlr-f5-plugin-code-climate-url]: https://codeclimate.com/github/xebialabs-community/xlr-f5-plugin
[xlr-f5-plugin-license-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[xlr-f5-plugin-license-url]: https://opensource.org/licenses/MIT
[xlr-f5-plugin-downloads-image]: https://img.shields.io/github/downloads/xebialabs-community/xlr-f5-plugin/total.svg



## Overview
#### GTM:
Global traffic manager (GTM) integration with Xl release gives an option to enable and disable datacenters of choice. GTM gives you full control on the release flow.

#### LTM:
Local traffic manager (LTM) integration with Xl release gives an option to enable and disable pool-member in a specific pool whithout shutting down pool itself.
It also gives you an option to enable/disable  multiple pool members.


## Installation
Copy the plugin JAR file into the `SERVER_HOME/plugins` directory of XL Release.
Install Python 2.7.x and the additional [pycontrol](https://pypi.python.org/pypi/pycontrol) and [suds](https://pypi.python.org/pypi/suds) libraries on the xl release server.
This plugin is mean to run the python script on the xl release windows server.

### Configuring Template

#### Enable LTM
![enableLTM](images/enableLTM.png)
#### Disable LTM
![disableLTM](images/disableLTM.png)
#### Enable GTM
![enableGTM](images/enableGTM.png)
#### Disable GTM
![disableGTM](images/disableGTM.png)

---
## References:
* https://devcentral.f5.com/wiki/iControl.LocalLB.ashx
* https://devcentral.f5.com/wiki/iControl.GlobalLB.ashx
