# Scheduler

`Scheduler` determines the optimal number of `wraps`, as well as the processes and threads in each wrap, based on `Profiler` and `Predictor`.

We provide implementations for native threads, Intel MPK and process pool, respectively.

* [Native threads](https://github.com/ykiauz/Chiron/tree/main/Scheduler/native)
* Intel MPK
  + [MPK-S](https://github.com/ykiauz/Chiron/tree/main/Scheduler/mpk-s)
  + [MPK-L](https://github.com/ykiauz/Chiron/tree/main/Scheduler/mpk-l)
* [Process Pool](https://github.com/ykiauz/Chiron/tree/main/Scheduler/pp)