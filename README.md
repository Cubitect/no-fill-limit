# no-fill-limit
Remove the 32768 block limit of /fill in Minecraft by hacking the java bytecode.

## Features

This script creates a copy of any minecraft java version and modifies the copy, raising the /fill limit to 2147483647. The mod can be created for servers or clients that use a pre-2.0 launcher.

## Usage

*NOTE*: For Windows and Minecraft Launcher 2.0+, you will need to install the mod to a server as the modified json file for clients won't work.

Make sure you have run the mincraft version for which you want to install this mod at least once, so that the .jar and .json files are present.

Then open a terminal/command line at the location of the python script and run:

`python no_fill_limit.py ~/.minecraft/versions/1.13-nolimit "1.13-nolimit" ~/.minecraft/versions/1.13/1.13.jar ~/.minecraft/versions/1.13/1.13.json`

Just replace any occurance of `1.13` with whatever version you would like. If you specify no command line arguments you will be prompted for the necessary information.

*NOTE*: For *servers* use the same procedure as for clients but leave the last argument (the json file) blank. E.g.:

`python no_fill_limit.py . server-nolimit server.jar`



