tmux-batteries
==============

A set of status indicators for tmux.

* `weather.py`: Displays temperature and weather condition.
* `system.py`: A reimplementation of `creaktive/rainbarf` in Python 3.
  Displays system information such as CPU and memory usages.

Requirements
------------

* `pip3 install psutil`

Install
-------

* Clone repository, add the following line to `~/.tmux.conf`

    ```
    set -g status-right '#(~/.external/tmux-batteries/weather.py) #(~/.external/tmux-batteries/system.py)'
    ```

Screenshots
-----------

![GitHub Logo](/screenshots/1.png)
