# pydatalog
This is a tool to read out the USB temperature data logger "RC-4". It's sold
under many brands ("Elitech" and "Floureaon" seem to be the most common at the
time of this writing). They appears to always be the same (white-label) device,
containing a CP2102 USB to UART Bridge Controller and therefore getting detected
by a Linux system as /dev/ttyUSBx.

![RC-4 Data Logger](https://raw.githubusercontent.com/johndoe31415/pydatalog/master/docs/rc4.jpg)

With pydatalog, you can configure and read out the data from these devices. The
protocol has been reverse engineered from the horrific, horrific original
software, so support may not be complete for all features.

# Usage
First, attach the device to your PC and identify which USB tty it was detected
as. Check that the device is recognized:

```
$ ./pyrc4datalog info
State           : READY
Station ID      : 1
Current datetime: 2018-06-30 12:55:07 (-0 seconds diff to UTC)
Last access     : 2018-06-30 12:50:54
Start datetime  : 2018-06-15 12:35:22
User info       : Kühltruhe
Device ID       : 1
Data points     : 0
Interval time   : 60 secs
Alarm min       : -30.0
Alarm max       : 60.0
Temperature cal : 0.0
Delay time      : 0.0 hrs
```

It's a good idea to sync the time to UTC first, then configure it as you see fit:

```
$ ./pyrc4datalog synctime
$ ./pyrc4datalog setinfo --user "Living Room"
$ ./pyrc4datalog setup --interval 10 -vv
2018-06-30 14:57:03,734 - pydatalog.ActionSetup - DEBUG - Logging interval set to 10 seconds
2018-06-30 14:57:03,734 - pydatalog.ActionSetup - INFO - Acquisition duration: 1 day, 20:26:40
2018-06-30 14:57:03,734 - pydatalog.ActionSetup - INFO - End of acquisition: 2018-07-02 11:23:43 (local)
```

Then, let the device log for a while. After you're done, you can readout all
data from it:

```
$ ./pyrc4datalog download --format txt -o my_room.txt
$ head -n 14 my_room.txt
# Readout of RC-4 device on 2018-06-30 13:00:10 UTC
# Device ID          : 1
# User Info          : Living Room
# Data points        : 16
# Interval time      : 10 secs
# Start of data      : 2018-06-30 12:57:32
# End of data        : 2018-06-30 13:00:09
# Unit of acquisition: °C

1530363452	2018-06-30 12:57:32	30.2
1530363462	2018-06-30 12:57:42	30.2
1530363472	2018-06-30 12:57:52	30.2
1530363482	2018-06-30 12:58:02	30.2
1530363492	2018-06-30 12:58:12	30.2
```

You can then continue to use that data as you see fit.

## Bug reporting
Be sure to include a verbose dump of all the exchanged data when you submit a
bug report, i.e., have "-vvv" as a command line option. This will cause a
hexdump of everything that is sent to/received from the RC-4.

## Dependencies
pydatalog requires Python3 and pyserial. To plot data using dataplot, you will
need Python3, pytz, tzlocal and (if requested) GnuPlot.

## License
GNU GPL-3.
