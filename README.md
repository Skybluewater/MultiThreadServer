# MultiThreadServer
A multi-thread web server implemented by Python with no frame

mainThread and mainThread2 是多线程服务器的2种不同实现方法(控制最大连接数为20并且清除最早的socket连接)

mainThread3和clientServer3是错误写法，具体错误在于（我也不懂，大概是因为一个全局变量在一个文件中的使用不会影响到另一个文件的全局变量，或者是出现预加载的问题

MD 玄学问题它来了

import a 和from import 之后如果发生修改, from import 会新建一个变量, 而a.threadNumber 不会

但为啥单纯就是这个出了问题而别的都没出问题呢

考研加油！
