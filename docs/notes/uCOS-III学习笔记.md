# uCOS-III学习笔记 ✏️⭐️

# 创建任务

这里创建的单个任务使用的栈和任务控制块都使用静态内存，即预先定义好的全局变量，这些预先定义好的全局变量都存在内部的 SRAM 中。



## 1. 定义任务栈 

若只创建一个任务，当此任务进入延时的时候，因为没有另外就绪的用户任务，那么系统就会进入空闲任务，**空闲任务是 uCOS 系统自己创建并且启动的一个任务，优先级最低。当整个系统都没有就绪任务的时候，系统必须保证有一个任务在运行，空闲任务就是为这个设计的**。当用户任务延时到期，又会从空闲任务切换回用户任务。

在 uCOS 系统中，每一个任务都是独立的，他们的运行环境都单独的保存在他们的栈空间当中。那么在定义好任务函数之后，我们还要为任务定义一个栈，因为目前使用的是静态内存，所以任务栈是一个独立的全局变量。任务的栈占用的是 MCU 内部的 RAM，当任务越多的时候，需要使用的栈空间就越大，即需要使用的 RAM 空间就越多。

定义任务栈及大小

```c
#define APP_TASK_START_STK_SIZE 128
static  CPU_STK  AppTaskStartStk[APP_TASK_START_STK_SIZE];
```



## 2. 定义任务控制块

定义好任务函数和任务栈之后，还需要为任务定义一个任务控制块，通常称这个任务控制块为任务的身份证。在 C 代码上，任务控制块就是一个**结构体**，里面有非常多的成员，这些成员共同描述了任务的全部信息。

定义任务控制块;

```c
static OS_TCB AppTaskStartTCB; 
```



## 3. 定义任务主体函数

任务实际上就是一个无限循环且不带返回值的 C 函数。下面创建一个这样的任务，让 LED 灯每隔 500ms 翻转一次。

```c
static void LED_Task (void* parameter)
{
    while (1)
    {
        LED1_ON;
        OSTimeDly (500,OS_OPT_TIME_DLY,&err); /* 延时500 个tick */

        LED1_OFF;
        OSTimeDly (500,OS_OPT_TIME_DLY,&err); /* 延时500 个tick */

    }
}
```

**任务必须是一个死循环**，否则任务将通过 LR 返回，如果 LR 指向了 非法的内存 就会 产生 HardFault_Handler ， 而 uCOS 指 向一个任务退出函数 OS_TaskReturn()，它如果支持任务删除的话，则进行任务删除操作，否则就进入死循环中，这样子的任务是不安全的，所以避免这种情况，任务一般都是死循环并且无返回值的，只执行一次的任务在执行完毕要记得及时删除。

**任务里面的延时函数必须使用 uCOS 里面提供的阻塞延时函数**，并不能使用裸机编程中的那种延时。这两种的延时的区别是：

- uCOS 里面的延时是**阻塞延时**，即调用 OSTimeDly() 函数的时候，**当前任务会被挂起，调度器会切换到其它就绪的任务，从而实现多任务**。
- 如果还是使用裸机编程中的那种延时，那么整个任务就成为了一个**死循环**，如果恰好该任务的优先级是最高的，那么系统永远都是在这个任务中运行，**比它优先级更低的任务无法运行**，根本无法实现多任务，因此任务中必须有能阻塞任务的函数，才能切换到其他任务中。



## 4. 创建任务

一个任务的三要素是任务主体函数、任务栈和任务控制块，uCOS 提供任务创建函数 OSTaskCreate()，它将任务主体函数，任务栈和任务控制块这三者联系在一起，让任务在创建之后可以随时被系统启动与调度。

创建任务：

```c
OSTaskCreate((OS_TCB *)&AppTaskStartTCB, 								(1) 
             (CPU_CHAR *)"App Task Start", 								(2) 
             (OS_TASK_PTR ) AppTaskStart, 								(3)  
             (void *) 0, 												(4) 
             (OS_PRIO ) APP_TASK_START_PRIO, 							(5)  
             (CPU_STK *)&AppTaskStartStk[0], 							(6) 
             (CPU_STK_SIZE) APP_TASK_START_STK_SIZE / 10,				(7)  
             (CPU_STK_SIZE) APP_TASK_START_STK_SIZE,				 	(8) 
             (OS_MSG_QTY ) 5u,											(9) 
             (OS_TICK ) 0u, 											(10) 
             (void *) 0, 												(11) 
             (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR), (12) 
             (OS_ERR *)&err);           								(13)
```

(1)：**任务控制块**，由用户自己定义。 

(2)：任务名字，字符串形式，这里任务名字最好要与任务函数入口名字一致，方便进行调试。 

(3)：**任务入口函数**，即任务函数的名称，需要我们自己定义并且实现。

(4)：**任务入口函数形参**，不用的时候配置为 0 或者 NULL 即可，p_arg 是指向可选数据区域的指针，用于将参数传递给任务，因为任务一旦执行，那必须是在一个死循环中，所以传参只在首次执行时有效。 

(5)：**任务的优先级**，由用户自己定义。

(6)：**指向堆栈基址的指针**（即堆栈的起始地址）。

(7)：设置堆栈深度的限制位置。这个值表示任务的堆栈满溢之前剩余的堆栈容量。例如，指定 stk_size 值的 10％表示将达到堆栈限制，当堆栈达到 90％满就表示任务的堆栈已满。 

(8)：**任务堆栈大小**，单位由用户决定，如果 CPU_STK 被设置为CPU_INT08U，则单位为字节，而如果 CPU_STK 被设置为 CPU_INT16U，则单位为半字，同理，如果 CPU_STK 被设置为 CPU_INT32U，单位为字。在 32 位的处理器下（STM32），
一个字等于4 个字节，那么任务大小就为 APP_TASK_START_STK_SIZE * 4 字节。 

(9)：**设置可以发送到任务的最大消息数**，按需设置即可。

(10)：在任务之间循环时的**时间片的时间量（以滴答为单位）。指定 0 则使用默认值**。 

(11)：是指向用户提供的内存位置的指针，用作 TCB 扩展。例如，该用户存储器可以保存浮点寄存器的内容在上下文切换期间，每个任务执行的时间，次数、任务已经切换等。 

(12)：用户可选的任务特定选项

```c
#define OS_OPT_TASK_NONE (OS_OPT)(0x0000u)    // 未选择任何选项
#define OS_OPT_TASK_STK_CHK (OS_OPT)(0x0001u) // 启用任务的堆栈检查
#define OS_OPT_TASK_STK_CLR (OS_OPT)(0x0002u) // 任务创建时清除堆栈
#define OS_OPT_TASK_SAVE_FP (OS_OPT)(0x0004u) // 保存任何浮点寄存器的内容，这需要 CPU 硬件的支持，CPU 需要有浮点运算硬件与专门保存浮点类型数据的寄存器。
#define OS_OPT_TASK_NO_TLS (OS_OPT)(0x0008u)  // 指定任务不需要 TLS 支持
```

(13)：用于保存返回的错误代码



## 5. 启动任务

**当任务创建好后，是处于任务就绪，在就绪态的任务可以参与操作系统的调度**。任务调度器只启动一次，之后就不会再次执行了，uCOS 中**启动任务调度器**的函数是 OSStart()，并且启动任务调度器的时候就不会返回，从此任务都由 uCOS 管理，此时才是真正进入实时操作系统中的第一步。

```c
/* 启动任务，开启调度 */ 
OSStart(&err);    
```



## 6. 代码示例

把任务主体，任务栈，任务控制块这三部分代码统一放到 app.c 中，在app.c 文件中创建一个 AppTaskStart 任务，这个任务是仅是用于测试用户任务，以后为了方便管理，所有的任务创建都统一放在这个任务中，在这个任务中创建成功的任务就可以直接参与任务调度了。

```c
#include <includes.h>

/*
*********************************************************************************************************
*                                            LOCAL DEFINES
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                                 TCB
*********************************************************************************************************
*/
static  OS_TCB   AppTaskStartTCB;

/*
*********************************************************************************************************
*                                                STACKS
*********************************************************************************************************
*/
static  CPU_STK  AppTaskStartStk[APP_TASK_START_STK_SIZE];

/*
*********************************************************************************************************
*                                         FUNCTION PROTOTYPES
*********************************************************************************************************
*/
static  void  AppTaskStart  (void *p_arg);

/*
*********************************************************************************************************
*                                                main()
*********************************************************************************************************
*/

int  main (void)
{
    OS_ERR  err;

    OSInit(&err);                                               /* Init uC/OS-III.                                      */

    OSTaskCreate((OS_TCB     *)&AppTaskStartTCB,                /* Create the start task                                */
                 (CPU_CHAR   *)"App Task Start",
                 (OS_TASK_PTR ) AppTaskStart,
                 (void       *) 0,
                 (OS_PRIO     ) APP_TASK_START_PRIO,
                 (CPU_STK    *)&AppTaskStartStk[0],
                 (CPU_STK_SIZE) APP_TASK_START_STK_SIZE / 10,
                 (CPU_STK_SIZE) APP_TASK_START_STK_SIZE,
                 (OS_MSG_QTY  ) 5u,
                 (OS_TICK     ) 0u,
                 (void       *) 0,
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR),
                 (OS_ERR     *)&err);

    OSStart(&err);                                              /* Start multitasking (i.e. give control to uC/OS-III). */
}

/*
*********************************************************************************************************
*                                          STARTUP TASK
*********************************************************************************************************
*/
static  void  AppTaskStart (void *p_arg)
{
    CPU_INT32U  cpu_clk_freq;
    CPU_INT32U  cnts;
    OS_ERR      err;

    (void)p_arg;

    BSP_Init();                                                 /* Initialize BSP functions                             */
    CPU_Init();

    cpu_clk_freq = BSP_CPU_ClkFreq();                           /* Determine SysTick reference freq.                    */
    cnts = cpu_clk_freq / (CPU_INT32U)OSCfg_TickRate_Hz;        /* Determine nbr SysTick increments                     */
    OS_CPU_SysTickInit(cnts);                                   /* Init uC/OS periodic time src (SysTick).              */

    Mem_Init();                                                 /* Initialize Memory Management Module                  */

    #if OS_CFG_STAT_TASK_EN > 0u
    OSStatTaskCPUUsageInit(&err);                               /* Compute CPU capacity with no task running            */
    #endif

    CPU_IntDisMeasMaxCurReset();


    while (DEF_TRUE) {                                          /* Task body, always written as an infinite loop.       */
        macLED1_TOGGLE ();
        OSTimeDly ( 5000, OS_OPT_TIME_DLY, & err );
    }	
}
```



# uCOS-III 启动流程

## 1. 系统初始化

在调用创建任务函数之前，我们必须要对系统进行一次初始化，而系统的初始化是根据我们配置宏定义进行初始化的，有一些则是系统必要的初始化，如空闲任务，时钟节拍任务等。

系统初始化函数 OSInit() 源代码（删减）：

```c
void OSInit (OS_ERR  *p_err) 
{ 
    CPU_STK      *p_stk; 
    CPU_STK_SIZE  size; 

    if (p_err == (OS_ERR *)0) { 
        OS_SAFETY_CRITICAL_EXCEPTION(); 
        return; 
    }

    OSInitHook(); /*初始化钩子函数相关的代码*/ 

    OSIntNestingCtr= (OS_NESTING_CTR)0; /*清除中断嵌套计数器*/ 

    OSRunning =  OS_STATE_OS_STOPPED;  /*未启动多任务处理*/ 

    OSSchedLockNestingCtr = (OS_NESTING_CTR)0; /* 清除锁定计数器*/ 

    OSTCBCurPtr= (OS_TCB *)0; /* 将OS_TCB 指针初始化为已知状态 */ 
    OSTCBHighRdyPtr = (OS_TCB *)0; 

    OSPrioCur = (OS_PRIO)0; /*将优先级变量初始化为已知状态*/ 
    OSPrioHighRdy                   = (OS_PRIO)0; 
    OSPrioSaved                     = (OS_PRIO)0; 

    if (OSCfg_ISRStkSize > (CPU_STK_SIZE)0) { 
        p_stk = OSCfg_ISRStkBasePtr; /* 清除异常堆栈以进行堆栈检查 */ 
        if (p_stk != (CPU_STK *)0) { 
            size  = OSCfg_ISRStkSize; 
            while (size > (CPU_STK_SIZE)0) { 
                size--; 
                *p_stk = (CPU_STK)0; 
                p_stk++; 
            } 
        } 
    }

    OS_PrioInit(); /* 初始化优先级位图表 */  

    OS_RdyListInit(); /*初始化就绪列表*/ 

    OS_TaskInit(p_err); /*初始化任务管理器 */  
    if (*p_err != OS_ERR_NONE) { 
        return; 
    }

    OS_IdleTaskInit(p_err); /* ★ 初始化空闲任务 */ (1)  
    if (*p_err != OS_ERR_NONE) { 
        return; 
    }

    OS_TickTaskInit(p_err); /* ★ 初始化时钟节拍任务 */ (2) 
    if (*p_err != OS_ERR_NONE) { 
        return; 
    }

    OSCfg_Init(); 
}
```

主要看两个地方，一个是空闲任务的初始化，一个是时钟节拍任务的初始化，这两个任务是必须存在的任务，否则系统无法正常运行。

其实空闲任务初始化就是创建一个空闲任务，空闲任务的相关信息由系统默认指定，用户不能修改。

OS_IdleTaskInit() 源码：

```c
void  OS_IdleTaskInit (OS_ERR  *p_err)
{
#ifdef OS_SAFETY_CRITICAL
    if (p_err == (OS_ERR *)0) {
        OS_SAFETY_CRITICAL_EXCEPTION();
        return;
    }
#endif

    OSIdleTaskCtr = (OS_IDLE_CTR)0;
                                                            /* ---------------- CREATE THE IDLE TASK ---------------- */
    OSTaskCreate((OS_TCB     *)&OSIdleTaskTCB,
                 (CPU_CHAR   *)((void *)"uC/OS-III Idle Task"),
                 (OS_TASK_PTR)OS_IdleTask,
                 (void       *)0,
                 (OS_PRIO     )(OS_CFG_PRIO_MAX - 1u),
                 (CPU_STK    *)OSCfg_IdleTaskStkBasePtr,
                 (CPU_STK_SIZE)OSCfg_IdleTaskStkLimit,
                 (CPU_STK_SIZE)OSCfg_IdleTaskStkSize,
                 (OS_MSG_QTY  )0u,
                 (OS_TICK     )0u,
                 (void       *)0,
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR | OS_OPT_TASK_NO_TLS),
                 (OS_ERR     *)p_err);
}
```

- OSIdleTaskCtr 在 os.h 头文件中定义，是一个 32 位无符号整型变量，该变量的作用是统计空闲任务的运行，现在初始化空闲任务，系统就将OSIdleTaskCtr 清零。
- 系统只是调用了 OSTaskCreate() 函数来创建一个 任 务 ， 这个任务就是空闲任务 ， 任 务优先级为OS_CFG_PRIO_MAX-1 ，
  OS_CFG_PRIO_MAX 是一个宏，该宏定义表示 uCOS 的任务优先级数值的最大值，在 uCOS 系统中，任务的优先级数值越大，表示任务的优先级越低，所以**空闲任务的优先级是最低的**。空闲任务堆栈大小为 OSCfg_IdleTaskStkSize，它也是一个宏，在os_cfg_app.c 文件中定义，默认为 128，则空闲任务堆栈默认为 128*4=512 字节。 

空闲任务其实就是一个函数，其函数入口是 OS_IdleTask。

OS_IdleTask() 源码：

```c
void  OS_IdleTask (void  *p_arg)
{
    CPU_SR_ALLOC();

    p_arg = p_arg;              /* Prevent compiler warning for not using 'p_arg'         */

    while (DEF_ON) {
        CPU_CRITICAL_ENTER();
        OSIdleTaskCtr++;
#if OS_CFG_STAT_TASK_EN > 0u
        OSStatTaskCtr++;
#endif
        CPU_CRITICAL_EXIT();

        OSIdleTaskHook();       /* Call user definable HOOK                               */
    }
}
```

空闲任务**是一个无限的死循环**，因为其优先级是最低的，所以**任何优先级比它高的任务都能抢占它从而取得 CPU 的使用权**，为什么系统要空闲任务呢？因为 「CPU 是不会停下来的，即使啥也不干，CPU 也不会停下来，此时系统就必须保证有一个随时处于就绪态的任务，而且这个任务不会抢占其他任务」。当且仅当系统的其他任务处于阻塞中，系统才会运行空闲任务，这个任务可以做很多事情，任务统计，钩入用户自定义的钩子函数实现用户自定义的功能等，但是需要注意的是，在钩子函数中用户不允许调用任何可以使空闲任务阻塞的函数接口，**空闲任务是不允许被阻塞的**。 



OS_TickTaskInit() 函数实际上也是创建一个时钟节拍任务：

```c
void  OS_TickTaskInit (OS_ERR  *p_err)
{
#ifdef OS_SAFETY_CRITICAL
    if (p_err == (OS_ERR *)0) {
        OS_SAFETY_CRITICAL_EXCEPTION();
        return;
    }
#endif

    OSTickCtr         = (OS_TICK)0u;   /* Clear the tick counter */

    OSTickTaskTimeMax = (CPU_TS)0u;


    OS_TickListInit();                 /* Initialize the tick list data structures */

    /* ---------------- CREATE THE TICK TASK ---------------- */
    if (OSCfg_TickTaskStkBasePtr == (CPU_STK *)0) {
       *p_err = OS_ERR_TICK_STK_INVALID;
        return;
    }

    if (OSCfg_TickTaskStkSize < OSCfg_StkSizeMin) {
       *p_err = OS_ERR_TICK_STK_SIZE_INVALID;
        return;
    }

    if (OSCfg_TickTaskPrio >= (OS_CFG_PRIO_MAX - 1u)) { /* Only one task at the 'Idle' priority */
       *p_err = OS_ERR_TICK_PRIO_INVALID;
        return;
    }

    OSTaskCreate((OS_TCB     *)&OSTickTaskTCB,
                 (CPU_CHAR   *)((void *)"uC/OS-III Tick Task"),
                 (OS_TASK_PTR )OS_TickTask,
                 (void       *)0,
                 (OS_PRIO     )OSCfg_TickTaskPrio,
                 (CPU_STK    *)OSCfg_TickTaskStkBasePtr,
                 (CPU_STK_SIZE)OSCfg_TickTaskStkLimit,
                 (CPU_STK_SIZE)OSCfg_TickTaskStkSize,
                 (OS_MSG_QTY  )0u,
                 (OS_TICK     )0u,
                 (void       *)0,
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR | OS_OPT_TASK_NO_TLS),
                 (OS_ERR     *)p_err);
}
```



## 2. CPU 初始化

在 main() 函数中，除了需要对板级硬件进行初始化，还需要进行一些系统相关的初始化，如 CPU 的初始化，在 uCOS 中，有一个很重要的功能就是**时间戳**，它的精度高达 **ns** 级别，是 CPU 内核的一个资源，所以使用的时候要对 CPU 进行相关的初始化。

CPU初始化函数 CPU_Init() 源码：

```c
void  CPU_Init (void)
{
    /* --------------------- INIT TS ---------------------- */
    #if ((CPU_CFG_TS_EN == DEF_ENABLED) || \
 		(CPU_CFG_TS_TMR_EN == DEF_ENABLED))
    CPU_TS_Init(); /* 时间戳测量的初始化 */ 
    #endif
    
    /* -------------- INIT INT DIS TIME MEAS -------------- */
    #ifdef  CPU_CFG_INT_DIS_MEAS_EN
    CPU_IntDisMeasInit(); /* 最大关中断时间测量初始化 */ 
    #endif

    /* ------------------ INIT CPU NAME ------------------- */
    #if (CPU_CFG_NAME_EN == DEF_ENABLED)
    CPU_NameInit(); //CPU 名字初始化
    #endif
}
```

在 Cortex-M（注意：M0 内核不可用）内核中有一个外设叫 DWT(Data Watchpoint and Trace)，是用于系统调试及跟踪，它有一个 32 位的寄存器叫 CYCCNT，它是一个向上的计数器，记录的是内核时钟运行的个数，内核时钟跳动一次，该计数器就加 1，当 CYCCNT 溢出之后，会清 0 重新开始向上计数。CYCCNT 的精度非常高，其精度取决于内核的频率是多少，如果是 STM32F1 系列，内核时钟是 72M，那精度就是 1/72M = 14ns，而程序的运行时间都是微秒级别的，所以 14ns 的精度是远远够的。

 uCOS 的时间戳的初始化函数 CPU_TS_TmrInit() 源码：

```c
#define  DWT_CR      *(CPU_REG32 *)0xE0001000
#define  DWT_CYCCNT  *(CPU_REG32 *)0xE0001004
#define  DEM_CR      *(CPU_REG32 *)0xE000EDFC

#define  DEM_CR_TRCENA                   (1 << 24) 

#define  DWT_CR_CYCCNTENA                (1 <<  0) 

#if (CPU_CFG_TS_TMR_EN == DEF_ENABLED)
void  CPU_TS_TmrInit (void)
{
    CPU_INT32U  cpu_clk_freq_hz;

    DEM_CR         |= (CPU_INT32U)DEM_CR_TRCENA; /* Enable Cortex-M3's DWT CYCCNT reg.                   */
    DWT_CYCCNT      = (CPU_INT32U)0u;
    DWT_CR         |= (CPU_INT32U)DWT_CR_CYCCNTENA;

    cpu_clk_freq_hz = BSP_CPU_ClkFreq();
    CPU_TS_TmrFreqSet(cpu_clk_freq_hz);
}
#endif
```



## 3. SysTick 初始化

**时钟节拍的频率表示操作系统每 1 秒钟产生多少个 tick**，tick 即是操作系统节拍的时钟周期，时钟节拍就是系统以固定的频率产生中断（时基中断），并在中断中处理与时间相关的事件，推动所有任务向前运行。时钟节拍需要**依赖于硬件定时器**，在 STM32 裸机程序中经常使用的 SysTick 时钟是 MCU 的内核定时器， 通常都使用该定时器产生操作系统的时钟节拍。用户需要先在 “os_cfg_app.h” 中设定时钟节拍的频率，**频率越高，操作系统检测事件就越频繁，可以增强任务的实时性，但太频繁也会增加操作系统内核的负担**，所以用户需要权衡该频率的设置。默认为 1000 Hz，也就是时钟节拍的周期为 1 ms。

函数 OS_CPU_SysTickInit() 用于初始化时钟节拍中断，初始化中断的优先级，SysTick 中断的使能等等，此函数要根据不同的 CPU 进行编写，并且**在系统任务的第一个任务开始的时候进行调用，如果在此之前进行调用，可能会造成系统奔溃，因为系统还没有初始化好就进入中断，可能在进入和退出中断的时候会调用系统未初始化好的一些模块**。

OS_CPU_SysTickInit() 源码：

```c
void  OS_CPU_SysTickInit (CPU_INT32U  cnts)
{
    CPU_INT32U  prio;

    /* 填写 SysTick 的重载计数值 */
    CPU_REG_NVIC_ST_RELOAD = cnts - 1u;                //SysTick 以该计数值为周期循环计数定时

    /* 设置 SysTick 中断优先级 */                           
    prio  = CPU_REG_NVIC_SHPRI3;                            
    prio &= DEF_BIT_FIELD(24, 0);
    prio |= DEF_BIT_MASK(OS_CPU_CFG_SYSTICK_PRIO, 24); //设置为默认的最高优先级0，在裸机例程中该优先级默认为最低

    CPU_REG_NVIC_SHPRI3 = prio;

    /* 使能 SysTick 的时钟源和启动计数器 */                   
    CPU_REG_NVIC_ST_CTRL |= CPU_REG_NVIC_ST_CTRL_CLKSOURCE |
                            CPU_REG_NVIC_ST_CTRL_ENABLE;
    /* 使能 SysTick 的定时中断 */                            
    CPU_REG_NVIC_ST_CTRL |= CPU_REG_NVIC_ST_CTRL_TICKINT;
}
```

在初始化任务中调用 OS_CPU_SysTickInit() 初始化系统时钟：

```c
static  void  AppTaskStart (void *p_arg)
{
    CPU_INT32U  cpu_clk_freq;
    CPU_INT32U  cnts;
    OS_ERR      err;

    (void)p_arg;

    BSP_Init();                                           //板级初始化
    CPU_Init();                                           //初始化 CPU 组件（时间戳、关中断时间测量和主机名）

    cpu_clk_freq = BSP_CPU_ClkFreq();                     //获取 CPU 内核时钟频率（SysTick 工作时钟）
    cnts = cpu_clk_freq / (CPU_INT32U)OSCfg_TickRate_Hz;  //根据用户设定的时钟节拍频率计算 SysTick 定时器的计数值
    OS_CPU_SysTickInit(cnts);                             //★ 调用 SysTick 初始化函数，设置定时器计数值和启动定时器

    ...

    OSTaskDel ( 0, & err );                     //删除起始任务本身，该任务不再运行
}
```



## 4. 内存初始化

内存在嵌入式中是很珍贵的存在，而一个系统它是软件，则必须要有一块内存属于系统所管理的。**uCOS 采 用 一 块 连 续 的 大 数 组 作 为 系 统 管 理 的 内 存 ， CPU_INT08U Mem_Heap[LIB_MEM_CFG_HEAP_SIZE]，在使用之前就需要先将管理的内存进行初始化**。

```c
static  void  AppTaskStart (void *p_arg)
{
    CPU_INT32U  cpu_clk_freq;
    CPU_INT32U  cnts;
    OS_ERR      err;

    (void)p_arg;

    BSP_Init();                                           //板级初始化
    CPU_Init();                                           //初始化 CPU 组件（时间戳、关中断时间测量和主机名）

    cpu_clk_freq = BSP_CPU_ClkFreq();                     //获取 CPU 内核时钟频率（SysTick 工作时钟）
    cnts = cpu_clk_freq / (CPU_INT32U)OSCfg_TickRate_Hz;  //根据用户设定的时钟节拍频率计算 SysTick 定时器的计数值
    OS_CPU_SysTickInit(cnts);                             //调用 SysTick 初始化函数，设置定时器计数值和启动定时器

    Mem_Init();                                           //★ 初始化内存管理组件（堆内存池和内存池表）
    ...

    OSTaskDel ( 0, & err );                     //删除起始任务本身，该任务不再运行
}
```



## 5. OSStart()

在创建完任务的时候，需要开启调度器，因为**创建仅仅是把任务添加到系统中，还没真正调度**。uCOS 提供了一个系统启动的函数接口——OSStart()，使用OSStart() 函数就能让系统开始运行。

```c
void  OSStart (OS_ERR  *p_err)
{
#ifdef OS_SAFETY_CRITICAL
    if (p_err == (OS_ERR *)0) {
        OS_SAFETY_CRITICAL_EXCEPTION();
        return;
    }
#endif

    if (OSRunning == OS_STATE_OS_STOPPED) {
        OSPrioHighRdy   = OS_PrioGetHighest();              /* Find the highest priority                              */
        OSPrioCur       = OSPrioHighRdy;
        OSTCBHighRdyPtr = OSRdyList[OSPrioHighRdy].HeadPtr;
        OSTCBCurPtr     = OSTCBHighRdyPtr;
        OSRunning       = OS_STATE_OS_RUNNING;
        OSStartHighRdy();                                   /* Execute target specific code to start task             */
       *p_err           = OS_ERR_FATAL_RETURN;              /* OSStart() is not supposed to return                    */
    } else {
       *p_err           = OS_ERR_OS_RUNNING;                /* OS is already running                                  */
    }
}
```

在主函数中调用 OSStart() 启动系统：

```c
int  main (void)
{
    OS_ERR  err;
    OSInit(&err);                                          //初始化 uC/OS-III

    /* 创建起始任务 */
    OSTaskCreate((OS_TCB     *)&AppTaskStartTCB,           //任务控制块地址
                 (CPU_CHAR   *)"App Task Start",           //任务名称
                 (OS_TASK_PTR ) AppTaskStart,              //任务函数
                 (void       *) 0,                         //传递给任务函数（形参p_arg）的实参
                 (OS_PRIO     ) APP_TASK_START_PRIO,       //任务的优先级
                 (CPU_STK    *)&AppTaskStartStk[0],        //任务堆栈的基地址
                 (CPU_STK_SIZE) APP_TASK_START_STK_SIZE / 10,  //任务堆栈空间剩下1/10时限制其增长
                 (CPU_STK_SIZE) APP_TASK_START_STK_SIZE,       //任务堆栈空间（单位：sizeof(CPU_STK)）
                 (OS_MSG_QTY  ) 5u,               //任务可接收的最大消息数
                 (OS_TICK     ) 0u,               //任务的时间片节拍数（0表默认值OSCfg_TickRate_Hz/10）
                 (void       *) 0,                //任务扩展（0表不扩展）
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR), //任务选项
                 (OS_ERR     *)&err);                                       //返回错误类型

    OSStart(&err);                     						//★ 启动多任务管理（交由uC/OS-III控制）
}
```



当在 AppTaskStart 中创建的应用任务的优先级比 AppTaskStart 任务的优先级高、低或者相等时候，程序是如何执行的？

- 若在临界区中创建任务，任务只能在退出临界区的时候才执行最高优先级任务。
- 假如没使用临界区的话，就会分三种情况： 

1. 应用任务的优先级比初始任务的优先级高，那创建完后立马去执行刚刚创建的应用任务，当应用任务被阻塞时，继续回到初始任务被打断的地方继续往下执行，直到所有应用任务创建完成，最后初始任务把自己删除，完成自己的使命；
2. 应用任务的优先级与初始任务的优先级一样，那创建完后根据任务的时间片来执行，直到所有应用任务创建完成，最后初始任务把自己删除，完成自己的使命；
3. 应用任务的优先级比初始任务的优先级低，那创建完后任务不会被执行，如果还有应用任务紧接着创建应用任务，如果应用任务的优先级出现了比初始任务高或者相等的情况，请参考 1 和 2 的处理方式，直到所有应用任务创建完成，最后初始任务把自己删除，完成自己的使命。

在调用 OSStart() 函数启动任务调度器的时候，假如启动成功的话，任务就不会有返回了，假如启动没成功，则通过 LR 寄存器指定的地址退出，在创建 AppTaskStart 任务的时候，任务栈对应 LR 寄存器指向是任务退出函数 OS_TaskReturn()，当系统启动没能成功的话，系统就不会运行。 



# 任务管理

## 1. 任务的基本概念

在任何时刻，只有一个任务得到运行，uCOS 调度器决定运行哪个任务。调度器会不断的启动、停止每一个任务，宏观看上去所有的任务都在同时在执行。每个 uCOS 任务都需要有自己的栈空间。当任务切出时，它的执行环境会被保存在该任务的栈空间中，这样当任务再次运行时，就能从堆栈中正确的恢复上次的运行环境，任务越多，需要的堆栈空间就越大，而一个系统能运行多少个任务，取决于系统的可用的 SRAM。

uCOS 中的任务采用**抢占式调度机制**，高优先级的任务可打断低优先级任务，低优先级任务必须在高优先级任务阻塞或结束后才能得到调度。



## 2. 任务调度器的基本概念

uCOS 中提供的任务调度器是**基于优先级的全抢占式调度**：在系统中除了中断处理函数、调度器上锁部分的代码和禁止中断的代码是不可抢占的之外，系统的其他部分都是可以抢占的。系统理论上可以支持无数个优先级(0 ～ N)，优先级数值越大的任务优先级越低，(OS_CFG_PRIO_MAX - 1u) 为最低优先级，分配给空闲任务使用，一般不建议用户来使用这个优先级。一般系统默认的最大可用优先级数目为 32。

一个操作系统如果只是具备了高优先级任务能够“立即”获得处理器并得到执行的特点，那么它仍然不算是实时操作系统。因为这个**查找最高优先级任务的过程决定了调度时间是否具有确定性**。

uCOS 内核中采用**两种方法寻找最高优先级的任务**：

- 第一种是通用的方法，因为 uCOS防止 CPU 平台不支持前导零指令，就**采用 C 语言模仿前导零指令**的效果实现了快速查找到最高优先级任务的方法。

- 而第二种方法则是特殊方法，**利用硬件计算前导零指令 CLZ**，这样子一次就能知道哪一个优先级任务能够运行，这种调度算法比普通方法更快捷，但受限于平台（在 STM32 中我们就使用这种方法）。 

如果分别创建了优先级 3 、5 、8 和 11 这四个任务，任务创建成功后，调用CPU_CntLeadZeros()可以计算出 OSPrioTbl[0]第一个置 1 的位前面有 3 个 0，那么这个 3 就是我们要查找的最高优先级，至于后面还有多少个位置 1 我们都不用管，只需要找到第一个 1 即可。 

uCOS 内核中也允许创建相同优先级的任务。**相同优先级的任务采用时间片轮转方式进行调度**（也就是通常说的分时调度器），时间片轮转调度仅在当前系统中无更高优先级就绪任务存在的情况下才有效。为了保证系统的实时性，系统**尽最大可能地保证高优先级的任务得以运行**。任务调度的原则是一旦任务状态发生了改变，并且当前运行的任务优先级小于优先级队列组中任务最高优先级时，立刻进行任务切换（除非当前系统处于中断处理程序中或禁止任务切换的状态）。



## 3. 任务状态迁移

uCOS 系统中的每一个任务都有多种运行状态，任务间状态转移具体见下图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620130337.png" width="400px" /> </div>

(1)：创建任务→就绪态（Ready）：任务创建完成后进入就绪态，表明任务已准备就绪，随时可以运行，只等待调度器进行调度。

(2)：就绪态→运行态（Running）：发生任务切换时，就绪列表中最高优先级的任务被执行，从而进入运行态。 

(3)：运行态→就绪态：有更高优先级任务创建或者恢复后，会发生任务调度，此刻就绪列表中最高优先级任务变为运行态，那么原先运行的任务由运行态变为就绪态，依然在就绪列表中，等待最高优先级的任务运行完毕继续运行原来的任务（此处可以看做是 CPU 使用权被更高优先级的任务抢占了）。

(4)：运行态→阻塞态（或者称为挂起态 Suspended）：正在运行的任务发生阻塞（挂起、延时、读信号量等待）时，该任务会从就绪列表中删除，任务状态由运行态变成阻塞态，然后发生任务切换，运行就绪列表中当前最高优先级任务。

(5)：阻塞态→就绪态：阻塞的任务被恢复后（任务恢复、延时时间超时、读信号量超时或读到信号量等），此时被恢复的任务会被加入就绪列表，从而由阻塞态变成就绪态；如果此时被恢复任务的优先级高于正在运行任务的优先级，则会发生任务切换，将该任务将再次转换任务状态，由就绪态变成运行态。 

(6) (7) (8)：就绪态、阻塞态、运行态→删除态（Delete）：任务可以通过调用 OSTaskDel() API 函数都可以将处于任何状态的任务删除，被删除后的任务将不能再次使用，关于任务的资源都会被系统回收。

(9)：删除态→就绪态：这就是创建任务的过程，一个任务将会从无到有，创建成功的任务可以参与系统的调度。
注意：此处的任务状态只是大致的任务状态而并非 uCOS 的所有任务状态，下面会具体介绍 uCOS 中具体的任务的状态。



## 4. 任务状态

uCOS 系统中每一任务都有多种运行状态。系统初始化完成后，创建的任务就可以在系统中竞争一定的资源，由内核进行调度。

uCOS 的任务状态通常分为以下几种： 

- **就绪**（OS_TASK_STATE_RDY）：该任务在就绪列表中，就绪的任务已经具备执行的能力，只等待调度器进行调度，新创建的任务会初始化为就绪态。 
- **延时**（OS_TASK_STATE_DLY）：该任务处于延时调度状态。 
- **等待**（OS_TASK_STATE_PEND）：任务调用 OSQPend()、OSSemPend()这类等待函数，系统就会设置一个超时时间让该任务处于等待状态，如果超时时间设置为 0，任务的状态，无限期等下去，直到事件发生。如果超时时间为 N(N>0)，在N 个时间内任务等待的事件或信号都没发生，就退出等待状态转为就绪状态。 
- **运行**（Running）：该状态表明任务正在执行，此时它占用处理器，UCOS 调度器选择运行的永远是处于最高优先级的就绪态任务，当任务被运行的一刻，它的任务状态就变成了运行态，其实运行态的任务也是处于就绪列表中的。
- **挂起**（OS_TASK_STATE_SUSPENDED）：任务通过调用OSTaskSuspend()函数能够 挂起自己或其他任务，调用OSTaskResume()是使被挂起的任务恢复运行的唯一的方法。挂起一任务意味着该任务再被恢复运行以前不能够取得CPU的使用权，类似强行暂停一个任务。
- **延时+挂起**（OS_TASK_STATE_DLY_SUSPENDED）：任务先产生一个延时，延时没结束的时候被其他任务挂起，挂起的效果叠加，当且仅当延时结束并且挂起 被恢复了，该任务才能够再次运行。
- **等待+挂起**（OS_TASK_STATE_PEND_SUSPENDED）：任务先等待一个事件或信号的发生（无限期等待），还没等待到就被其他任务挂起，挂起的效果叠加，当且仅当任务等待到事件或信号并且挂起被恢复了，该任务才能够再次运行。
- **超时等待+挂起**（OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED）：任务在指定时间内等待事件或信号的产生，但是任务已经被其他任务挂起。
- **删除**（OS_TASK_STATE_DEL）：任务被删除后的状态，任务被删除后将不再运行，除非重新创建任务。 



## 5. 任务的常用函数

### 任务挂起函数OS_TaskSuspend()

任务可以通过调用 OS_TaskSuspend() 函数**将处于任何状态的任务挂起**，**被挂起的任务得不到 CPU 的使用权，也不会参与调度，不管该任务具有什么优先级**。它相对于调度器而言是不可见的，除非它从挂起态中解除。

- 如果的任务是当前任务，也就是挂起任务自身，那么需要判断一下调度器有没有被锁定，因为挂起任务自身之后，就肯定需要切换任务，而如果调度器被 锁定的话，就无法切换任务了，所以会返回错误类型 “调度器被锁”，然后退出。
- 如果任务处于就绪状态，那么该任务能直接挂起，但是接下来**要操作就绪列表，时间是不确定的**，我们**不能将中断关闭太久，这样子会影响系统对中断的响应**，此时系统就会打开中断，但是系统又不想其他任务来影响我们操作就绪列表，
  所以系统还会**锁定调度器**，不进行任务切换，这样子就不会有任务打扰我们的操作了，然后将任务状态变为挂起态，然后调用 OS_RdyListRemove() 函数将任务从就绪列表移除，再打开调度器，然后跳出，最后才进行任务的调度。
- 任务可以调用 OS_TaskSuspend() 这个函数来挂起任务自身，但是在挂起自身的时候**会进行一次任务上下文切换**，需要挂起自身就将任务控制块指针设置为 NULL 或 0 传递进来即可。无论任务是什么状态都可以被挂起，只要调用了OS_TaskSuspend() 这个函数就会挂起成功，不论是挂起其他任务还是挂起任务自身。



### 任务恢复函数OSTaskResume()

任务恢复就是**让挂起的任务重新进入就绪状态**，恢复的任务会保留挂起前的状态信息，在恢复的时候根据挂起时的状态继续运行。如果被恢复任务在所有就绪态任务中，处于最高优先级列表的第一位，那么系统将进行任务上下文的切换。

- 如果禁用了中断延迟发布和中断中非法调用检测，那么在中断中恢复任务则是非法的，会直接返回错误类型为 “在中断中恢复任务”，并且退出。而如果使能了中断延迟发布的话呢，就可以在中断中恢复任务，因为中断延迟发布的真正操作是
  在中断发布任务中。
- 如果使能了中断延迟发布，并且如果该函数在中断中被调用，系统就会把恢复任务命令发布到中断消息队列中，唤醒中断发布任务，在任务中恢复指定任务，并且退出。
- OSTaskResume() 函数用于恢复挂起的任务。任务在挂起时候调用过多少次的OS_TaskSuspend() 函数，那么就需要调用多少次 OSTaskResume() 函数才能将任务恢复运行。



### 删除任务函数OSTaskDel()

OSTaskDel()用于删除一个任务。当一个任务删除另外一个任务时，形参为要删除任务创建时返回的任务句柄，如果是删除自身，则形参为NULL。删除的任务将从所有就绪，阻塞，挂起和事件列表中删除。

- 在中断中删除任务则是非法的。
- 不允许删除空闲任务。
- 如果使能了中断延迟发布，但是要删除的目标任务是中断延迟发布任务，这也是绝对不允许的，因为使能了中断延迟发布，则代表着系统中必须有一个中断延迟发布任务处理在中断中的发布的事情。
- 在删除任务的时候，系统还会调用用户自定义的钩子函数，用户可以通过该钩子函数进行自定义的操作。
- 注意：删除任务并不会释放任务的堆栈空间。



### 任务延时函数OSTimeDly() / OSTimeDlyHMSM()

任务延时的可选选项有：

- OS_OPT_TIME_DLY：dly 为相对时间，就是从现在起延时多长时 间 ， 到 时 钟 节 拍 总 计 数 OSTickCtr = OSTickCtr 当前 + dly 时延时结束。
- OS_OPT_TIME_TIMEOUT：跟 OS_OPT_TIME_DLY 的作用情况一样。
- OS_OPT_TIME_MATCH：dly 为绝对时间，就是从系统开始运行（调用 OSStart()） 时到节拍总计数OSTickCtr = dly 时延时结束。
- OS_OPT_TIME_PERIODIC ： 周 期 性 延 时 ， 跟 OS_OPT_TIME_DLY 的作用差不多，如果是长时间延时，该选项更精准一些。



OSTimeDly()在我们任务中用得非常之多，**每个任务都必须是死循环**，并且是必须要有阻塞的情况，否则低优先级的任务就无法被运行了，OSTimeDly() 函数常**用于停止当前任务的运行，延时一段时间后再运行**。

- 延时函数**不可在中断中使用**。
- 如果**调度器被锁，则不允许进行延时操作**。因为延时就必须进行任务的切换，所以在延时的时候不能锁定调度器
- 需要调用OS_TickListInsert() 函数将当前任务插入到节拍列表，加入节拍列表的任务会按照延时时间进行升序排列。其中会使用到哈希算法（取余）来决定任务存储到节拍列表中的位置。
- OSTimeDly() 使用示例：

```c
void AppTask(void * p_arg)
{
    OS_ERR err;
 while (DEF_TRUE) {
        //  这里为任务主体代码

        /* 调用相对延时函数, 阻塞1000 个tick */
        OSTimeDly(1000, OS_OPT_TIME_DLY, &err);
 }
}
```



OSTimeDlyHMSM() 函数与 OSTimeDly() 函数的功能类似，也是用于停止当前任务进行的运行，延时一段时间后再运行，但是 OSTimeDlyHMSM() 函数会更加直观，延时多少个小时、分钟、秒、毫秒。

- OSTimeDlyHMSM() 使用示例：

```c
void AppTask(void * p_arg)
{
    OS_ERR err;
    while (DEF_TRUE) {
        //  这里为任务主体代码

        /* 调用延时函数, 延时1s */
        OSTimeDlyHMSM(0,0,1,0, OS_OPT_TIME_DLY, &err);
    }
}
```



## 6. 任务的设计要点

uCOS 中程序运行的上下文包括： 

- 中断服务函数
  - 中断服务函数是一种需要特别注意的上下文环境，它**运行在非任务的执行环境下**（一般为芯片的一种特殊运行模式（也被称作特权模式）），在这个上下文环境中**不能使用挂起当前任务的操作**，不允许调用任何会阻塞运行的 API 函数接口。另外需要注意的是，中断服务程序最好**保持精简短小，快进快出**，一般在中断服务函数中只做标记事件的发生，然后通知任务，让对应任务去执行相关处理，因为中断服务函数的优先级高于任何优先级的任务，如果中断处理时间过长，将会导致整个系统的任务无法正常运行。所以在设计的时候必须考虑中断的频率、中断的处理时间等重要因素，以便配合对应中断处理任务的工作。
  - uCOS 支持**中断延迟发布**，使得**原本在中断中发布的信息变成任务级发布**，这样子会使得中断服务函数的处理更加快速，屏蔽中断的时间更短，这样子能快速响应其他的中断，真正称得上实时操作系统。
- 普通任务
  - 任务看似没有什么限制程序执行的因素，似乎所有的操作都可以执行。但是做为一个优先级明确的实时系统，**如果一个任务中的程序出现了死循环操作（此处的死循环是指没有阻塞机制的任务循环体），那么比这个任务优先级低的任务都将无法执行**，当然也包括了空闲任务，因为死循环的时候，任务不会主动让出 CPU，低优先级的任务是不可能得到CPU 的使用权的，而高优先级的任务就可以抢占 CPU。这个情况在实时操作系统中是必须注意的一点，所以**在任务中不允许出现死循环**。如果一个任务只有就绪态而无阻塞态，势必会影响到其他低优先级任务的执行，所以在进行任务设计时，就应该保证任务在不活跃的时候，任务可以进入阻塞态以交出 CPU 使用权，这就需要我们自己明确知道什么情况下让任务进入阻塞态，保证低优先级任务可以正常运行。在实际设计中，一般会将紧急的处理事件的任务优先级设置得高一些。
- 空闲任务
  - 空闲任务（idle 任务）是 uCOS 系统中没有其他工作进行时自动进入的系统任务。因为处理器总是需要代码来执行——所以**至少要有一个任务处于运行态**。uCOS 为了保证这一点，当调用 OSInit() 函数进行系统初始化时，系统会自动创建一个空闲任务，空闲任务是一个非常短小的循环。**用户可以通过空闲任务钩子方式，在空闲任务上钩入自己的功能函数**。通常这个空闲任务钩子能够完成一些额外的特殊功能，例如系统运行状态的指示，系统省电模式等。**空闲任务是唯一一个不允许出现阻塞情况的任务，因为 uCOS 需要保证系统永远都有一个可运行的任务**。
  - 对于空闲任务钩子上挂接的空闲钩子函数，它应该满足以下的条件：
    -  永远不会挂起空闲任务
    - 不应该陷入死循环，需要留出部分时间用于统计系统的运行状态等



# 消息队列

## 1. 消息队列的基本概念

消息队列可以在**任务与任务间、中断和任务间**传递信息，实现了任务接收来自其他任务或中断的**不固定长度**的消息，任务能够从队列里面读取消息，当队列中的消息是空时，读取消息的任务将被阻塞。用户还可以指定阻塞的任务时间 timeout，在这段时间中，如果队列为空，该任务将保持阻塞状态以等待队列数据有效。当队列中有新消息时，被阻塞的任务会被唤醒并处理新消息；当等待的时间超过了指定的阻塞时间，即使队列中尚无有效数据，任务也会自动从阻塞态转为就绪态。消息队列是一种**异步**的通信方式。

通过消息队列服务，任务或中断服务程序可以将消息放入消息队列中。同样，一个或多个任务可以从消息队列中获得消息。当有多个消息发送到消息队列时，uCOS支持FIFO或者LIFO将先进入/后进入消息队列的消息先传给任务。

uCOS 中使用队列数据结构实现**任务异步通信**工作，具有如下特性：

- 消息支持**先进先出**方式排队（FIFO），支持异步读写工作方式。
- 消息支持**后进先出**方式排队（LIFO），往队首发送消息。
- 读消息队列支持**超时机制**。
- 可以允许不同长度的**任意类型消息**（因为是引用方式传递，无论多大的数据都只是一个指针）。
- **一个任务能够从任意一个消息队列接收和发送消息**。
- **多个任务能够从同一个消息队列接收和发送消息**。
- 当队列使用结束后，可以通过删除队列函数进行删除。



## 2. 消息队列的工作过程

在 uCOS-III 中定义了一个数组 OSCfg_MsgPool[OS_CFG_MSG_POOL_SIZE]，因为**在使用消息队列的时候存取消息比较频繁**，在系统初始化的时候就将这个大数组的各个元素串成**单向链表**，组成我们说的**消息池**，而这些元素我们称之为消息。

> **使用单向链表的原因**：消息的存取并不需要从链表中间， 只需在链表的首尾存取即可，单向链表即够用，使用双向链表反而更复杂。

> **使用消息池的原因**：这样的处理很快，并且共用了资源，系统中所有被创建的队列都可以从消息池中取出消息，挂载到自身的队列上，以表示消息队列拥有消息，当消息使用完毕，则又会被释放回到消息池中，其他队列也可以从中取出消息，这样的消息资源是能被系统所有的消息队列反复使用。



### 2.1 消息池初始化

在系统初始化（OSInit() ）的时候，系统就会将消息池进行初始化，其中， OS_MsgPoolInit() 函数就是用来初始化消息池的。

- 系统会将消息池里的消息逐条串成单向链表，方便管理，通过 for循环将消息池中的每个消息元素（消息）进行初始化，并且通过单链表连接起来。
- 每个消息 OS_MSG 有四个元素：

```c
struct  os_msg {                   /* 消息控制块  */
    OS_MSG              *NextPtr;  /* 指向下一个可用的消息 */
    void                *MsgPtr;   /* 指向实际的消息 */
    OS_MSG_SIZE          MsgSize;  /* 记录消息的大小（以字节为单位）*/
    CPU_TS               MsgTS;    /* 记录发送消息时的时间戳 */
};
```

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620204357.png" width="200px" /> </div>

- OSMsgPool 是个全局变量，用来管理消息池的存取操作，它包含以下四个元素：

```c
struct  os_msg_pool {                /* 消息池控制块 */
    OS_MSG              *NextPtr;    /* 指向下一个可用的消息 */
    OS_MSG_QTY           NbrFree;    /* 记录消息池中可用的消息个数 */
    OS_MSG_QTY           NbrUsed; 	 /* 记录已用的消息个数 */
    OS_MSG_QTY           NbrUsedMax; /* 记录使用的消息峰值数量 */
};
```

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620204718.png" width="200px" /> </div>

- 初始化完成的消息池示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620204941.png" width="700px" /> </div>



### 2.2 消息队列的运作机制

uCOS 的消息队列控制块由多个元素组成，**当消息队列被创建时，编译器会静态为消息队列分配对应的内存空间**（因为我们需要自己定义一个消息队列控制块），用于保存消息队列的一些信息如队列的名字，队列可用的最大消息个数，入队指针、出队指针等。在创建成功的时候，这些内存就被占用了，创建队列的时候用户指定队列的最大消息个数，无法再次更改，每个消息空间可以存放任意类型的数据。  

**任务或者中断服务程序都可以给消息队列发送消息，当发送消息时，如果队列未满，uCOS 会将从消息池中取出一个消息，将消息挂载到队列的尾部，消息中的成员变量MsgPtr 指向要发送的消息**。如果队列已满，则返回错误代码，入队失败。

**uCOS 还支持发送紧急消息，也就是我们所说的后进先出（LIFO）排队**，其过程与发送消息几乎一样，唯一的不同是，当发送紧急消息时，发送的消息会**挂载到队列的队头而非队尾**，这样，接收者就能够优先接收到紧急消息，从而及时进行消息处理。

当某个任务试图读一个队列时，**可以指定一个阻塞超时时间**。在这段时间中，如果队列为空，该任务将保持阻塞状态以等待队列数据有效。当其它任务或中断服务程序往其等待的队列中写入了数据，该任务将自动由阻塞态转移为就绪态。当等待的时间超过了指定的阻塞时间，即使队列中尚无有效数据，任务也会自动从阻塞态转移为就绪态。

当消息队列不再被使用时，可以对它进行删除操作，一旦删除操作完成，消息队列将被永久性的删除，所有关于队列的信息会被清空，直到再次创建才可使用。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620205914.png" width="700px" /> </div>



## 3. 消息队列的阻塞机制

在很多时候，创建的队列， 是每个任务都可以去对他进行读写操作的，但是**为了保护每个任务对消息队列进行读操作的过程**（ uCOS 队列的写操作是没有阻塞的），**必须要有阻塞机制**，在某个任务对消息队列进行读操作的时候，必须保证该任务能正常完成读操作，而不受后来的任务干扰。

假设有一个任务 A 对某个队列进行读操作的时候（也就是我们所说的出队），发现它没有消息，那么此时任务 A 有 3 个选择：

- 第一个选择：任务 A **不等待**，这样子任务 A 不会进入阻塞态；
- 第二个选择：任务 A **进入阻塞状态**，等待着消息的到来。任务 A 的等待时间由我们自己定义，比如设置 1000 个系统时钟节拍 tick 的等待，在 这 1000 个 tick 到来之前任务 A 都是处于阻塞态，当阻塞的这段时间任务 A 等到了队列的消息，那么任务 A 就会从阻塞态变成就绪态，如果此时任务 A 比当前运行的任务优先级还高，那么，任务 A 就会得到消息并且运行；假如1000 个 tick 都过去了，队列还没消息，那任务 A 就不等了，从阻塞态中唤醒，返回一个没等到消息的错误代码，然后继续执行任务 A 的其他代码。
- 第三个选择：任务 A 死等，任务 A 进入阻塞态，直到完成读取队列的消息。

假如有多个任务阻塞在一个消息队列中，那么这些阻塞的任务将**按照任务优先级进行排序**，优先级高的任务将优先获得队列的访问权。

如果发送消息的时候用户选择**广播消息**，那么在等待中的任务都会收到一样的消息。



## 4. 消息队列的应用场景

消息队列可以**应用于发送不定长消息的场合**，包括任务与任务间的消息交换，队列是uCOS 中**任务与任务间、中断与任务间主要的通讯方式**，发送到队列的消息是通过**引用方式实现**的，这意味着队列存储的是数据的地址，我们可以通过这个地址将这个数据读取出来，这样子，*无论数据量是多大，其操作时间都是一定的*，只是一个指向数据地址指针。



## 5. 消息队列的结构

uCOS 的消息队列由多个元素组成，在消息队列被创建时，需要我们自己定义消息队列（也可以称之为消息队列句柄），因为它是用于保存消息队列的一些信息的，其数据结构 **OS_Q 除了队列必须的一些基本信息外，还有 PendList 链表与 MsgQ**，为的是方便系统来管理消息队列。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620215030.png" width="200px" /> </div>

OS_Q 的定义：

```c
struct  os_q {                       /* 消息队列 */
                                     /* ------------------ GENERIC  MEMBERS ------------------ */
    OS_OBJ_TYPE          Type;       /* 消息队列的类型 OS_OBJ_TYPE_Q */
    CPU_CHAR            *NamePtr;    /* 消息队列的名字 */
    OS_PEND_LIST         PendList;   /* 等待消息队列的任务列表 */
#if OS_CFG_DBG_EN > 0u
    OS_Q                *DbgPrevPtr;
    OS_Q                *DbgNextPtr;
    CPU_CHAR            *DbgNamePtr;
#endif
                                     /* ------------------ SPECIFIC MEMBERS ------------------ */
    OS_MSG_Q             MsgQ;       /* 消息列表 */
};
```

OS_MSG_Q 的定义：

```c
struct  os_msg_q {                        /* OS_MSG_Q */
    OS_MSG              *InPtr;           /* 指向要插入队列的下一个OS_MSG 的指针 */
    OS_MSG              *OutPtr;          /* 指向要从队列中提取的下一个OS_MSG 的指针 */
    OS_MSG_QTY           NbrEntriesSize;  /* 队列中允许的最大消息个数 */
    OS_MSG_QTY           NbrEntries;      /* 队列中当前的消息个数 */
    OS_MSG_QTY           NbrEntriesMax;   /* 队列中的消息个数峰值 */
};
```

队列中消息也是用**单向链表**串联起来的，但**存取消息不像消息池只是从固定的一端**。队列存取消息有两种方式：

- 一种是 FIFO 模式，即先进先出，这个时候消息的存取是在单向链表的两端，一个头一个尾，存取位置可能不一样就产生了这两个输入指针和输出指针。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625163047.png" width="700px" /> </div>

- 另一种是 LIFO 模式，后进先出，这个时候消息的存取都是在单向链表的一端，仅仅用 OutPtr 就足够指示存取的位置，当队列中已经存在比较多的消息没有处理，这个时候有个**紧急的消息**需要马上传送到其他任务去的时候就可以在发布消息的时候选择 LIFO 模式。 

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200620215801.png" width="700px" /> </div>



## 6. 消息队列的常用函数

### 创建消息队列函数OSQCreate()

- 每创建一个新的队列都需要为其分配 RAM，在创建的时候我们需要自己定义一个消息队列结构体，其内存是由编译器自动分配的。
- 消息队列的阻塞列表用于记录阻塞在此消息队列上的任务。
- 定义了队列的句柄（结构体）并不等于创建了队列，创建队列必须时调用消息队列创建函数进行创建，否则，以后根据队列句柄使用消息队列的其它函数时会发生错误，用户通过消息队列句柄就可使用消息队列进行发送与获取消息的操作。
- 消息队列创建示例：

```c
OS_Q  queue; //声明消息队列
OS_ERR      err;
/* 创建消息队列 queue */
OSQCreate ((OS_Q         *)&queue,            //指向消息队列的指针
           (CPU_CHAR     *)"Queue For Test",  //队列的名字
           (OS_MSG_QTY    )20,                //最多可存放消息的数目
           (OS_ERR       *)&err);             //返回错误类型
```



### 消息队列删除函数OSQDel()

队列删除函数是根据队列结构（队列句柄）直接删除的，删除之后这个消息队列的所有信息都会被系统清空，而且不能再次使用这个消息队列了。需要注意的是，**如果某个消息队列没有被定义，那也是无法被删除的**。如果删除消息队列时，有任务正在等待消息，则不应该进行删除操作，删除之后的消息队列就不可用了。

- 如果任务是就绪状态、延时状态、挂起状态或者是在延时中被挂起，这些任务状态均与等待内核对象是无关的，在内核对象被删除的时候无需进行任何操作。
- 如果任务是无期限等待状态或者是有期限等待状态，那么在内核对象被删除的时候需要将这些任务恢复。
- 如果任务在无期限等待中被挂起或者在有期限等待中被挂起，也是需要将这些等待内核对象的任务从等待中移除，但是由于在等待中被挂起，那么就不会将这些任务恢复为就绪态，仅仅是将任务从等待列表中移除。

```c
OS_Q queue; //声明消息队列
OS_ERR err;
/* 删除消息队列 queue */
OSQDel ((OS_Q *)&queue, //指向消息队列的指针
        OS_OPT_DEL_NO_PEND,
        (OS_ERR *)&err); //返回错误类型
```



### 消息队列发送函数OSQPost()

**任务或者中断服务程序**都可以给消息队列发送消息，当发送消息时，如果队列未满， 就说明运行信息入队。uCOS-III会**从消息池中取出一个消息**，挂载到消息队列的**末尾**（FIFO 发送方式），如果是LIFO发送方式，则将消息挂载到消息队列的**头部**，然后**将消息中 MsgPtr 成员变量指向要发送的消息**（此处可以理解为添加要发送的信息到消息（块）中），如果系统有任务阻塞在消息队列中，那么在发送了消息队列的时候，会将任务解除阻塞。

> 我的理解：消息池就是提前创建好一些OS_MSG结构体的实例，后面需要创建消息时，直接从消息池中取出一个放入消息队列即可，通过修改NextPtr指针即可管理哪些消息实例属于当前消息队列。

发送消息的选项：

```c
#define OS_OPT_POST_FIFO (OS_OPT)(0x0000u) /* 默认采用FIFO 方式发送 */
#define OS_OPT_POST_LIFO (OS_OPT)(0x0010u) /* 采用LIFO 方式发送消息 */
#define OS_OPT_POST_1   (OS_OPT)(0x0000u)  /* 将消息发布到最高优先级的等待任务 */
#define OS_OPT_POST_ALL (OS_OPT)(0x0200u)  /* 向所有等待的任务广播消息 */

#define OS_OPT_POST_NO_SCHED (OS_OPT)(0x8000u) /* 发送消息但是不进行任务调度 */
```



OS_QPost() 函数源码：

```c
void  OS_QPost (OS_Q         *p_q,      //消息队列指针
                void         *p_void,   //消息指针
                OS_MSG_SIZE   msg_size, //消息大小（单位：字节）
                OS_OPT        opt,      //选项
                CPU_TS        ts,       //消息被发布时的时间戳
                OS_ERR       *p_err)    //返回错误类型
{
    OS_OBJ_QTY     cnt;
    OS_OPT         post_type;
    OS_PEND_LIST  *p_pend_list;
    OS_PEND_DATA  *p_pend_data;
    OS_PEND_DATA  *p_pend_data_next;
    OS_TCB        *p_tcb;
    CPU_SR_ALLOC();  //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                     //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                     // SR（临界段关中断只需保存SR），开中断时将该值还原。

    OS_CRITICAL_ENTER();                              //进入临界段
    p_pend_list = &p_q->PendList;                     //取出该队列的等待列表

    /* 如果有任务在等待该队列 */
    if (p_pend_list->NbrEntries == (OS_OBJ_QTY)0) {   //如果没有任务在等待该队列
        if ((opt & OS_OPT_POST_LIFO) == (OS_OPT)0) {  //把消息发布到队列的末端
            post_type = OS_OPT_POST_FIFO;
        } else {                                      //把消息发布到队列的前端
            post_type = OS_OPT_POST_LIFO;
        }
        OS_MsgQPut(&p_q->MsgQ,                        /* 把消息放入消息队列 */
                   p_void,
                   msg_size,
                   post_type,
                   ts,
                   p_err);
        OS_CRITICAL_EXIT();                          //退出临界段
        return;                                      //返回，执行完毕
    }

    /* 如果有任务在等待该队列 */
    if ((opt & OS_OPT_POST_ALL) != (OS_OPT)0) {     //如果要把消息发布给所有等待任务
        cnt = p_pend_list->NbrEntries;              //获取等待任务数目
    } else {                                        //如果要把消息发布给一个等待任务
        cnt = (OS_OBJ_QTY)1;                        //要处理的任务数目为1
    }
    p_pend_data = p_pend_list->HeadPtr;             //获取等待列表的头部（任务）
    while (cnt > 0u) {                              //根据要发布的任务数目逐个发布
        p_tcb            = p_pend_data->TCBPtr;
        p_pend_data_next = p_pend_data->NextPtr;
        OS_Post((OS_PEND_OBJ *)((void *)p_q),       /* 把消息发布给任务 */
                p_tcb,
                p_void,
                msg_size,
                ts);
        p_pend_data = p_pend_data_next;
        cnt--;
    }
    OS_CRITICAL_EXIT_NO_SCHED();                     //退出临界段（无调度）
    if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0) { //如果没选择“发布完不调度任务”
        OSSched();                                   //任务调度
    }
   *p_err = OS_ERR_NONE;                             //错误类型为“无错误”
}
```



- 没有任务等待就直接将消息放入队列中即可，而有任务在等待则有可能需要唤醒该任务。

  如果有任务在等待消息，会有两种情况：

  - 一种是将消息发送到所有等待任务（广播消息）。
  - 另一种是只将消息发送到等待任务中最高优先级的任务。根据 opt 选项选择其中一种方式进行发送消息，如果要把消息发送给所有等待任务，那就首先获取到等待任务个数，保存在要处理任务个数 cnt 变量中。



- OS_MsgQPut() 函数用于将消息放入队列中

```c
void  OS_MsgQPut(OS_MSG_Q     *p_msg_q,   //消息队列指针
                 void         *p_void,    //消息指针
                 OS_MSG_SIZE   msg_size,  //消息大小（单位：字节）
                 OS_OPT        opt,       //选项
                 CPU_TS        ts,        //消息被发布时的时间戳
                 OS_ERR       *p_err)     //返回错误类型
{
      OS_MSG  *p_msg;
      OS_MSG  *p_msg_in;
  
  
  #ifdef OS_SAFETY_CRITICAL                //如果使能了安全检测
      if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
          OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
          return;                          //返回，停止执行
      }
  #endif
  
      if (p_msg_q->NbrEntries >= p_msg_q->NbrEntriesSize) { //如果消息队列已没有可用空间
         *p_err = OS_ERR_Q_MAX;                             //错误类型为“队列已满”
          return;                                           //返回，停止执行
      }
  
      if (OSMsgPool.NbrFree == (OS_MSG_QTY)0) {  //如果消息池没有可用消息
         *p_err = OS_ERR_MSG_POOL_EMPTY;         //错误类型为“消息池没有消息”  
          return;                                //返回，停止执行
      }
      
      /* 从消息池获取一个消息（暂存于 p_msg ）*/
      p_msg             = OSMsgPool.NextPtr;          //将消息控制块从消息池移除               
      OSMsgPool.NextPtr = p_msg->NextPtr;             //指向下一个消息（取走首个消息）
      OSMsgPool.NbrFree--;                            //消息池可用消息数减1
      OSMsgPool.NbrUsed++;                            //消息池被用消息数加1
      
      if (OSMsgPool.NbrUsedMax < OSMsgPool.NbrUsed) { //更新消息被用最大数目的历史记录
          OSMsgPool.NbrUsedMax = OSMsgPool.NbrUsed;
      }
      
      /* 将获取的消息插入到消息队列 */
      if (p_msg_q->NbrEntries == (OS_MSG_QTY)0) {             //如果消息队列目前没有消息
          p_msg_q->InPtr         = p_msg;                     //将其入队指针指向该消息
          p_msg_q->OutPtr        = p_msg;                     //出队指针也指向该消息
          p_msg_q->NbrEntries    = (OS_MSG_QTY)1;             //队列的消息数为1
          p_msg->NextPtr         = (OS_MSG *)0;               //该消息的下一个消息为空
      } else {                                                //如果消息队列目前已有消息
          if ((opt & OS_OPT_POST_LIFO) == OS_OPT_POST_FIFO) { //如果用FIFO方式插入队列，
              p_msg_in           = p_msg_q->InPtr;            //将消息插入到入队端，入队
              p_msg_in->NextPtr  = p_msg;                     //指针指向该消息。
              p_msg_q->InPtr     = p_msg;
              p_msg->NextPtr     = (OS_MSG *)0;
          } else {                                            //如果用LIFO方式插入队列，
              p_msg->NextPtr     = p_msg_q->OutPtr;           //将消息插入到出队端，出队
              p_msg_q->OutPtr    = p_msg;                     //指针指向该消息。
          }
          p_msg_q->NbrEntries++;                              //消息队列的消息数目加1
      }
      
      if (p_msg_q->NbrEntriesMax < p_msg_q->NbrEntries) {     //更新改消息队列的最大消息
          p_msg_q->NbrEntriesMax = p_msg_q->NbrEntries;       //数目的历史记录。
      }
      p_msg->MsgPtr  = p_void;                                //给该消息填写消息内容
      p_msg->MsgSize = msg_size;                              //给该消息填写消息大小
      p_msg->MsgTS   = ts;                                    //填写发布该消息时的时间戳
     *p_err          = OS_ERR_NONE;                           //错误类型为“无错误”
  }
```

  - p_msg = OSMsgPool.NextPtr; 
  
    从消息池获取一个消息（暂存于 p_msg），OSMsgPool 是消息池，它的 NextPtr 成员变量指向消息池中可用的消息。
  
  - OSMsgPool.NextPtr = p_msg->NextPtr; 
  
    更新消息池中 NextPtr 成员变量，指向消息池中下一个可用的消息。
  
  - if (p_msg_q->NbrEntries == (OS_MSG_QTY)0)
  
    将获取的消息插入到消息队列时分两种情况：一种是队列中有消息情况，另一种是队列中没有消息情况。如果消息队列目前没有消息，将队列中的入队指针指向该消息，出队指针也指向该消息，因为现在消息放进来了，只有一个消息，无论是入队还是出队，都是该消息，更新队列的消息个数为 1，该消息的下一个消息为空。
  
  - if ((opt & OS_OPT_POST_LIFO) == OS_OPT_POST_FIFO) 
  
    如果消息队列目前已有消息，那么又分两种入队的选项：
    - 如果采用 FIFO 方式插入队列，那么就将消息插入到入队端，消息队列的最后一个消息的 NextPtr 指针就指向该消息，然后入队的消息成为队列中排队的最后一个消息，那么需要更新它的下一个消息为空。
    - 如果采用 LIFO 方式插入队列，将消息插入到出队端，队列中出队指针 OutPtr 指向该消息，需要出队的时候就是该消息首先出队。

  

- OS_Post() 函数负责把消息发送给任务

```c
void  OS_Post (OS_PEND_OBJ  *p_obj,     //内核对象类型指针
               OS_TCB       *p_tcb,     //任务控制块
               void         *p_void,    //消息
               OS_MSG_SIZE   msg_size,  //消息大小
               CPU_TS        ts)        //时间戳
{
    switch (p_tcb->TaskState) {                               //根据任务状态分类处理
        case OS_TASK_STATE_RDY:                               //如果任务处于就绪状态
        case OS_TASK_STATE_DLY:                               //如果任务处于延时状态
        case OS_TASK_STATE_SUSPENDED:                         //如果任务处于挂起状态
        case OS_TASK_STATE_DLY_SUSPENDED:                     //如果任务处于延时中被挂起状态
             break;                                           //不用处理，直接跳出

        case OS_TASK_STATE_PEND:                              //如果任务处于无期限等待状态
        case OS_TASK_STATE_PEND_TIMEOUT:                      //如果任务处于有期限等待状态
             if (p_tcb->PendOn == OS_TASK_PEND_ON_MULTI) {    //如果任务在等待多个信号量或消息队列
                 OS_Post1(p_obj,                              //标记哪个内核对象被发布
                          p_tcb,
                          p_void,
                          msg_size,
                          ts);
             } else {                                     //如果任务不是在等待多个信号量或消息队列
#if (OS_MSG_EN > 0u)                                      //如果使能了任务队列或消息队列
                 p_tcb->MsgPtr  = p_void;                 //保存消息到等待任务
                 p_tcb->MsgSize = msg_size;                   
#endif
                 p_tcb->TS      = ts;                     //保存时间戳到等待任务
             }
             if (p_obj != (OS_PEND_OBJ *)0) {             //如果内核对象为空
                 OS_PendListRemove(p_tcb);                /* 从等待列表移除该等待任务 */
#if OS_CFG_DBG_EN > 0u                                    //如果使能了调试代码和变量 
                 OS_PendDbgNameRemove(p_obj,              //移除内核对象的调试名
                                      p_tcb);
#endif
             }
             OS_TaskRdy(p_tcb);                               //让该等待任务准备运行
             p_tcb->TaskState  = OS_TASK_STATE_RDY;           //任务状态改为就绪状态
             p_tcb->PendStatus = OS_STATUS_PEND_OK;           //清除等待状态
             p_tcb->PendOn     = OS_TASK_PEND_ON_NOTHING;     //标记不再等待
             break;

        case OS_TASK_STATE_PEND_SUSPENDED:                    //如果任务在无期限等待中被挂起
        case OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED:            //如果任务在有期限等待中被挂起
             if (p_tcb->PendOn == OS_TASK_PEND_ON_MULTI) {    //如果任务在等待多个信号量或消息队列
                 OS_Post1(p_obj,                              //标记哪个内核对象被发布
                          p_tcb,
                          p_void,
                          msg_size,
                          ts);
             } else {                                       //如果任务不在等待多个信号量或消息队列
#if (OS_MSG_EN > 0u)                                        //如果使能了调试代码和变量
                 p_tcb->MsgPtr  = p_void;                   //保存消息到等待任务
                 p_tcb->MsgSize = msg_size;                     
#endif
                 p_tcb->TS      = ts;                         //保存时间戳到等待任务
             }
             OS_TickListRemove(p_tcb);                        /* 从节拍列表移除该等待任务 */
             if (p_obj != (OS_PEND_OBJ *)0) {                 //如果内核对象为空
                 OS_PendListRemove(p_tcb);                    /* 从等待列表移除该等待任务 */
#if OS_CFG_DBG_EN > 0u                                        //如果使能了调试代码和变量 
                 OS_PendDbgNameRemove(p_obj,                  //移除内核对象的调试名
                                      p_tcb);
#endif
             }
             p_tcb->TaskState  = OS_TASK_STATE_SUSPENDED;     //任务状态改为被挂起状态
             p_tcb->PendStatus = OS_STATUS_PEND_OK;           //清除等待状态
             p_tcb->PendOn     = OS_TASK_PEND_ON_NOTHING;     //标记不再等待
             break;

        default:                                              //如果任务状态超出预期
             break;                                           //直接跳出
    }
}
```

如果任务处于**就绪状态、延时状态、挂起状态或者是延时中被挂起状态**，都不用处理，直接退出，因为现在这个操作是内核对象进行发布（释放）操作，而这些状态的任务是与内核对象无关的状态，也就是这些任务没在等待相关的内核对象（如消息队列、信号量等）。

如果任务处于**无期限等待状态或者是有期限等待状态**，那么就需要处理了，先看看任务是不是在等待多个内核对象。

- 如果任务在等待多个信号量或消息队列，就调用 OS_Post1() 函数标记一下是哪个内核对象进行发布（释放）操作。

- 如果任务不是在等待多个信号量或消息队列，直接操作即可。如果使能了任务队列或消息队列（OS_MSG_EN宏定义），保存消息到等待任务控制块的 MsgPtr 成员变量中，将消息的大小保存到等待任务控制块的 MsgSize 成员变量中。 

- 如果内核对象不为空，调用 OS_PendListRemove() 函数**从等待列表移除该等待任务**。

如果任务在**无期限等待中被挂起，或者任务在有期限等待中被挂起**，反正任务就是在等待中被挂起了，也能进行内核对象发布（释放）操作。同理，先看看任务是不是在等待多个内核对象。 

- 如果任务在等待多个信号量或消息队列，就调用 OS_Post1() 函数标记一下是哪个内核对象进行发布（释放）操作。 
- 如果任务不在等待多个信号量或消息队列，就直接操作即可。
- 如果使能了任务队列或消息队列（使能了 OS_MSG_EN 宏定义），保存消息到等待任务控制块的 MsgPtr 成员变量中，将消息的大小保存到等待任务控制块的 MsgSize 成员变量中。 

调用OS_TickListRemove()函数将任务**从节拍列表中移除**。

从**等待列表移除**该等待任务。

任务状态改为被挂起状态。

清除任务的等待状态。

标记任务不再等待。



- OSQPost() 使用实例：

```c
/* 发布消息到消息队列 queue */
OSQPost ((OS_Q        *)&queue,            //消息变量指针
         (void        *)"Fire uC/OS-III",  //要发送的数据的指针，将内存块首地址通过队列“发送出去”
         (OS_MSG_SIZE  )sizeof ( "Fire uC/OS-III" ),        //数据字节大小
         (OS_OPT       )OS_OPT_POST_FIFO | OS_OPT_POST_ALL, //先进先出和发布给全部任务的形式
         (OS_ERR      *)&err);	                            //返回错误类型
```



### 消息队列获取函数OSQPend()

**当任务试图从队列中获取消息时，用户可以指定一个阻塞超时时间**，当且仅当消息队列中有消息的时候，任务才能获取到消息。在这段时间中，如果队列为空，该任务将保持阻塞状态以等待队列消息有效。当**其他任务或中断服务程序往其等待的队列中写入了数据**，该任务将自动由**阻塞态转为就绪态**。当**任务等待的时间超过了用户指定的阻塞时间**，即使队列中尚无有效消息，任务也会自动从**阻塞态转为就绪态**。

- 当获取消息不成功的时候，用户选择了阻塞等待，那么就会将任务状态变为阻塞态以等待消息。 

- 判断一下调度器是否被锁，如果被锁了，则返回错误类型为“调度器被锁”的错误代码，然后退出。 **如果调度器未被锁，就锁定调度器，重新打开中断**。

  - ⭐️为什么刚刚调度器被锁就错误，而现在又要锁定调度器？

    因为之前锁定的调度器不是被这个函数锁定的，这是不允许的。因为**现在要阻塞当前任务，而调度器锁定了就表示无法进行任务调度**。那为什么又要关闭调度器呢，因为**接下来的操作是需要操作队列与任务的列表，这个时间就不会很短，系统不希望有其他任务来操作任务列表，因为可能引起其他任务解除阻塞，这可能会发生优先级翻转**。比如任务 A 的优先级低于当前任务，但是在当前任务进入阻塞的过程中，任务 A 却因为其他原因解除阻塞了，那系统肯定是会去运行任务 A，这显然是要绝对禁止的，因为挂起调度器意味着任务不能切换并且不准调用可能引起任务切换的 API 函数，所以，**锁定调度器，打开中断这样的处理，既不会影响中断的响应，又避免了其他任务来操作队列与任务的列表**。 

```c
void  *OSQPend (OS_Q         *p_q,       //消息队列指针
                OS_TICK       timeout,   //等待期限（单位：时钟节拍）
                OS_OPT        opt,       //选项
                OS_MSG_SIZE  *p_msg_size,//返回消息大小（单位：字节）
                CPU_TS       *p_ts,      //获取等到消息时的时间戳
                OS_ERR       *p_err)     //返回错误类型
{
    OS_PEND_DATA  pend_data;
    void         *p_void;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((void *)0);             //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;               //错误类型为“在中断中中止等待”
        return ((void *)0);                    //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                //如果使能了参数检测
    if (p_q == (OS_Q *)0) {               //如果 p_q 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;      //错误类型为“对象为空”
        return ((void *)0);               //返回0（有错误），停止执行
    }
    if (p_msg_size == (OS_MSG_SIZE *)0) { //如果 p_msg_size 为空
       *p_err = OS_ERR_PTR_INVALID;       //错误类型为“指针不可用”
        return ((void *)0);               //返回0（有错误），停止执行
    }
    switch (opt) {                        //根据选项分类处理
        case OS_OPT_PEND_BLOCKING:        //如果选项在预期内
        case OS_OPT_PEND_NON_BLOCKING:
             break;                       //直接跳出

        default:                          //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;  //返回错误类型为“选项非法”
             return ((void *)0);          //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u        //如果使能了对象类型检测
    if (p_q->Type != OS_OBJ_TYPE_Q) {  //如果 p_q 不是消息队列类型
       *p_err = OS_ERR_OBJ_TYPE;       //错误类型为“对象类型有误”
        return ((void *)0);            //返回0（有错误），停止执行
    }
#endif

    if (p_ts != (CPU_TS *)0) {  //如果 p_ts 非空
       *p_ts  = (CPU_TS  )0;    //初始化（清零）p_ts，待用于返回时间戳
    }

    CPU_CRITICAL_ENTER();                                 //关中断
    p_void = OS_MsgQGet(&p_q->MsgQ,                       /* 从消息队列获取一个消息 */
                        p_msg_size,
                        p_ts,
                        p_err);
    if (*p_err == OS_ERR_NONE) {                          //如果获取消息成功
        CPU_CRITICAL_EXIT();                              //开中断
        return (p_void);                                  //返回消息内容
    }
    
    /* 如果获取消息不成功 !!!*/
    if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) {  //如果选择了不堵塞任务
        CPU_CRITICAL_EXIT();                              //开中断
       *p_err = OS_ERR_PEND_WOULD_BLOCK;                  //错误类型为“等待渴求堵塞”
        return ((void *)0);                               //返回0（有错误），停止执行
    } else {                                              //如果选择了堵塞任务
        if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) {  //如果调度器被锁
            CPU_CRITICAL_EXIT();                          //开中断
           *p_err = OS_ERR_SCHED_LOCKED;                  //错误类型为“调度器被锁”
            return ((void *)0);                           //返回0（有错误），停止执行
        }
    }
    
    /* 如果调度器未被锁 !!!*/                                
    OS_CRITICAL_ENTER_CPU_EXIT();                         //锁调度器，重开中断
    OS_Pend(&pend_data,                                   /* 堵塞当前任务，等待消息队列 */
            (OS_PEND_OBJ *)((void *)p_q),                 /* 将当前任务脱离就绪列表，并 */
            OS_TASK_PEND_ON_Q,                            /* 插入到节拍列表和等待列表。 */
            timeout);
    OS_CRITICAL_EXIT_NO_SCHED();                          //开调度器，但不进行调度

    OSSched();                                            //找到并调度最高优先级就绪任务
    
    /* 当前任务（获得消息队列的消息）得以继续运行 !!!*/
    CPU_CRITICAL_ENTER();                                 //关中断
    switch (OSTCBCurPtr->PendStatus) {                    //根据当前运行任务的等待状态分类处理
        case OS_STATUS_PEND_OK:                           //如果等待状态正常  
             p_void     = OSTCBCurPtr->MsgPtr;            //从（发布时放于）任务控制块提取消息
            *p_msg_size = OSTCBCurPtr->MsgSize;           //提取消息大小
             if (p_ts  != (CPU_TS *)0) {                  //如果 p_ts 非空
                *p_ts   =  OSTCBCurPtr->TS;               //获取任务等到消息时的时间戳
             }
            *p_err      = OS_ERR_NONE;                    //错误类型为“无错误”
             break;                                       //跳出

        case OS_STATUS_PEND_ABORT:                        //如果等待被中止
             p_void     = (void      *)0;                 //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                 //返回消息大小为0
             if (p_ts  != (CPU_TS *)0) {                  //如果 p_ts 非空
                *p_ts   =  OSTCBCurPtr->TS;               //获取等待被中止时的时间戳
             }
            *p_err      = OS_ERR_PEND_ABORT;              //错误类型为“等待被中止”
             break;                                       //跳出

        case OS_STATUS_PEND_TIMEOUT:                      //如果等待超时
             p_void     = (void      *)0;                 //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                 //返回消息大小为0
             if (p_ts  != (CPU_TS *)0) {                  //如果 p_ts 非空
                *p_ts   = (CPU_TS  )0;                    //清零 p_ts
             }
            *p_err      = OS_ERR_TIMEOUT;                 //错误类型为“等待超时”
             break;                                       //跳出

        case OS_STATUS_PEND_DEL:                          //如果等待的内核对象被删除
             p_void     = (void      *)0;                 //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                 //返回消息大小为0
             if (p_ts  != (CPU_TS *)0) {                  //如果 p_ts 非空
                *p_ts   =  OSTCBCurPtr->TS;               //获取对象被删时的时间戳
             }
            *p_err      = OS_ERR_OBJ_DEL;                 //错误类型为“等待对象被删”
             break;                                       //跳出

        default:                                          //如果等待状态超出预期
             p_void     = (void      *)0;                 //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                 //返回消息大小为0
            *p_err      = OS_ERR_STATUS_INVALID;          //错误类型为“状态非法”
             break;                                       //跳出
    }
    CPU_CRITICAL_EXIT();                                  //开中断
    return (p_void);                                      //返回消息内容
}
```



OS_MsgQGet() 函数从消息队列获取一个消息。

```c
void  *OS_MsgQGet (OS_MSG_Q     *p_msg_q,     //消息队列
                   OS_MSG_SIZE  *p_msg_size,  //返回消息大小
                   CPU_TS       *p_ts,        //返回某些操作的时间戳
                   OS_ERR       *p_err)       //返回错误类型
{
    OS_MSG  *p_msg;
    void    *p_void;

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((void *)0);             //返回空消息，停止执行
    }
#endif

    if (p_msg_q->NbrEntries == (OS_MSG_QTY)0) {  //如果消息队列没有消息
       *p_msg_size = (OS_MSG_SIZE)0;             //返回消息长度为0
        if (p_ts != (CPU_TS *)0) {               //如果 p_ts 非空
           *p_ts  = (CPU_TS  )0;                 //清零 p_ts
        }
       *p_err = OS_ERR_Q_EMPTY;                  //错误类型为“队列没消息”
        return ((void *)0);                      //返回空消息，停止执行
    }
    
    /* 如果消息队列有消息 !!!*/
    p_msg           = p_msg_q->OutPtr;          //从队列的出口端提取消息           
    p_void          = p_msg->MsgPtr;            //提取消息内容
   *p_msg_size      = p_msg->MsgSize;           //提取消息长度
    if (p_ts != (CPU_TS *)0) {                  //如果 p_ts 非空
       *p_ts  = p_msg->MsgTS;                   //获取消息被发布时的时间戳
    }

    p_msg_q->OutPtr = p_msg->NextPtr;           //修改队列的出队指针

    if (p_msg_q->OutPtr == (OS_MSG *)0) {       //如果队列没有消息了
        p_msg_q->InPtr      = (OS_MSG   *)0;    //清零出队指针
        p_msg_q->NbrEntries = (OS_MSG_QTY)0;    //清零消息数
    } else {                                    //如果队列还有消息
        p_msg_q->NbrEntries--;                  //队列的消息数减1
    }
    
    /* 从消息队列提取完消息信息后，将消息释放回消息池供继续使用 !!!*/
    p_msg->NextPtr    = OSMsgPool.NextPtr;      /* 消息插回消息池，以便重复利用 */
    OSMsgPool.NextPtr = p_msg;
    OSMsgPool.NbrFree++;                        //消息池的可用消息数加1
    OSMsgPool.NbrUsed--;                        //消息池的已用消息数减1

   *p_err             = OS_ERR_NONE;            //错误类型为“无错误”
    return (p_void);                            //返回罅隙内容
}
```



OS_Pend() 函数将当前任务脱离就绪列表，并根据用户指定的阻塞时间插入到节拍列表和队列等待列表，然后打开调度器，但不进行调度。

```c
void  OS_Pend (OS_PEND_DATA  *p_pend_data,  //待插入等待列表的元素
               OS_PEND_OBJ   *p_obj,        //等待的内核对象
               OS_STATE       pending_on,   //等待哪种对象内核
               OS_TICK        timeout)      //等待期限
{
    OS_PEND_LIST  *p_pend_list;

    OSTCBCurPtr->PendOn     = pending_on;                 //资源不可用，开始等待
    OSTCBCurPtr->PendStatus = OS_STATUS_PEND_OK;          //正常等待中

    OS_TaskBlock(OSTCBCurPtr,                             /* 阻塞当前运行任务 */
                 timeout);                                /* 如果timeout非0，把任务插入节拍列表 */

    if (p_obj != (OS_PEND_OBJ *)0) {                      //如果等待对象非空
        p_pend_list             = &p_obj->PendList;       //获取对象的等待列表到 p_pend_list
        p_pend_data->PendObjPtr = p_obj;                  //保存要等待的对象
        OS_PendDataInit((OS_TCB       *)OSTCBCurPtr,      /* 初始化p_pend_data（待插入等待列表）*/
                        (OS_PEND_DATA *)p_pend_data,
                        (OS_OBJ_QTY    )1);
        OS_PendListInsertPrio(p_pend_list,                /* 按优先级将p_pend_data插入到等待列表 */
                              p_pend_data);
    } else {                                                 //如果等待对象为空
        OSTCBCurPtr->PendDataTblEntries = (OS_OBJ_QTY    )0; //清零当前任务的等待域数据
        OSTCBCurPtr->PendDataTblPtr     = (OS_PEND_DATA *)0; 
    }
#if OS_CFG_DBG_EN > 0u                                       //如果使能了调试代码和变量 
    OS_PendDbgNameAdd(p_obj,                                 //更新信号量的 DbgNamePtr 元素为其等待
                      OSTCBCurPtr);                          //列表中优先级最高的任务的名称。
#endif
}
```



OSQPend() 使用实例

```c
OS_Q queue; //声明消息队列 

OS_ERR      err;
OS_MSG_SIZE msg_size;

/* 获取消息队列 queue 的消息 */ 
pMsg = OSQPend ((OS_Q         *)&queue,             //消息变量指针
                (OS_TICK       )0,                  //等待时长为无限
                (OS_OPT        )OS_OPT_PEND_BLOCKING,  //如果没有获取到信号量就等待
                (OS_MSG_SIZE  *)&msg_size,          //获取消息的字节大小
                (CPU_TS       *)0,                  //获取任务发送时的时间戳
                (OS_ERR       *)&err);              //返回错误
```



## 7. 消息队列使用注意事项

在使用 uCOS 提供的消息队列函数的时候，需要了解以下几点： 

1. 使用 OSQPend()、OSQPost() 等这些函数之前应先创建需消息队列，并根据队列句柄（队列控制块）进行操作。 

2. 队列读取采用的是先进先出（FIFO）模式，会先读取先存储在队列中的数据。当然也 uCOS 也支持后进先出（LIFO）模式，那么读取的时候就会读取到后进队列的数据。 

3. 无论是发送或者是接收消息都是以数据引用的方式进行。 
4. 队列是具有自己独立权限的内核对象，并不属于任何任务。所有任务都可以向同一队列写入和读出。一个队列由多任务或中断写入是经常的事，但由多个任务读出倒是用的比较少。 
5. **消息的传递实际上只是传递传送内容的指针和传送内容的字节大小**。这在使用消息队列的时候就要注意了，获取消息之前不能释放存储在消息中的指针内容，比如中断定义了一个局部变量，然后将其地址放在消息中进行传递，中断退出之前消息并没有被其他任务获取，退出中断的时候 CPU 已经释放了中断中的这个局部变量，后面任务获取这个地址的内容就会出错。所以**一定要保证在获取内容地址之前不能释放内容这个内存单元**。有三种方式可以避免这种情况： 

- 将变量**定义为静态变量**，即在其前面加上 static，这样内存单元就不会被释放。 

- 将变量**定义为全局变量**。 

- **将要传递的内容当做指针传递过去**。

  比如地址 0x12345678 存放一个变量的值为 5，常规是把 0x12345678 这个地址传递给接收消息的任务，任务接收到这个消息后，取出这个地址的内容 5。但是如果我们把 5 当做“地址”传递给任务，最后接收消息的任务直接拿着这个“地址”当做内容去处理即可。不过这种方法不能传递结构体等比较复杂的数据结构，因为消息中存放地址的变量内存大小是有限的（一个指针大小）。 



# 信号量

## 1\. 信号量基本概念

**信号量（Semaphore）是一种实现任务间通信的机制**，可以实现**任务之间同步**或**临界资源的互斥访问**，常用于协助一组相互竞争的任务来访问临界资源。在多任务系统中，各任务之间需要同步或互斥实现临界资源的保护，信号量功能可以为用户提供这方面的支持。 

抽象的来讲，信号量是一个非负整数，所有获取它的任务都会将该整数减一（获取它当然是为了使用资源），当该整数值为零时，所有试图获取它的任务都将处于阻塞状态。通常一个信号量的计数值用于对应有效的资源数，表示剩下可被占用的临界资源数，其值的含义分两种情况： 

- 0：表示没有积累下来的释放信号量操作，且有可能有在此信号量上阻塞的任务。 
- 正值，表示有一个或多个释放信号量操作。

**注意：uCOS 中的信号量不具备传递数据的功能。** 



### 二值信号量

二值信号量既可以用于**临界资源访问**也可以用于**同步**功能。 

二值信号量和互斥信号量（以下使用互斥量表示互斥信号量）非常相似，但是有一些细微差别：**互斥量有优先级继承机制，二值信号量则没有这个机制**。这使得二值信号量更偏向应用于同步功能（任务与任务间的同步或任务和中断间同步），而互斥量更偏向应用于临界资源的互斥访问。 

用作同步时，信号量在创建后应被置为空，任务 1 获取信号量而进入阻塞，任务 2 在某种条件发生后，释放信号量，于是任务 1 获得信号量得以进入就绪态，如果任务 1 的优先级是最高的，那么就会立即切换任务，从而达到了**两个任务间的同步**。同样的，**在中断服务函数中释放信号量，任务1 也会得到信号量，从而达到任务与中断间的同步**。

在裸机开发中我们经常是在中断中做一个标记，然后在退出的时候进行轮询处理，这个就是类似我们使用信号量进行同步的，当标记发生了，再做其他事情。**在 uCOS 中我们用信号量用于同步，任务与任务的同步，中断与任务的同步**，可以大大提高效率。 



### 计数信号量

在实际使用中，常将计数信号量用于**事件计数与资源管理**。每当某个事件发生时，**任务或者中断**将释放一个信号量（信号量计数值加 1），当处理被事件时（一般在任务中处理），处理任务会取走该信号量（信号量计数值减 1），**信号量的计数值则表示还有多少个事件没被处理。此外，系统还有很多资源，我们也可以使用计数信号量进行资源管理**，信号量的计数值表示系统中可用的资源数目，任务必须先获取到信号量才能获取资源访问权，当信号量的计数值为零时表示系统没有可用的资源，但是要注意，**在使用完资源的时候必须归还信号量**，否则当计数值为 0的时候任务就无法访问该资源了。 



## 2\. 信号量使用场景

**1、二值信号量是任务与任务、任务与中断间同步的重要手段**

在多任务系统中，经常会用到二值信号量，比如，某个任务需要等待一个标记，那么任务可以在**轮询**中查询这个标记有没有被置位，但是这样子做，就会很**消耗 CPU资源并且妨碍其它任务执行**。更好的做法是任务的大部分时间处于**阻塞**状态（允许其它任务执行），**直到某些事件发生该任务才被唤醒去执行**。可以使用二进制信号量实现这种同步，当任务取信号量时，因为此时尚未发生特定事件，信号量为空，任务会进入阻塞状态；当事件的条件满足后，任务/中断便会释放信号量，告知任务这个事件发生了，任务取得信号量便被唤醒去执行对应的操作，任务执行完毕并**不需要归还信号量**，这样子的 CPU 的效率可以大大提高，而且实时响应也是最快的。
再比如某个任务使用信号量等待中断的发生，在这之前任务已经进入了阻塞态，在等待着中断的发生，当在中断发生之后，释放一个信号量，也就是标记，在退出中断之后，操作系统会进行任务的调度，如果这个任务能够运行，系统就会去执行这个任务，这样子就大大提高了我们的效率。

- 二值信号量在**任务与任务**中同步的应用场景：

  假设我们有一个**温湿度传感器**，假设是 1s 采集一次数据，那么我们让他在**液晶屏**中显示数据出来，这个周期也是要 1s 一次的，**如果液晶屏刷新的周期是 100ms 更新一次，那么此时的温湿度的数据还没更新，液晶屏根本无需刷新**，只需要在 1s 后温湿度数据更新的时候刷新即可，否则 CPU 就是白白做了多次的无效数据更新，CPU 的资源就被刷新数据这个任务占用了大半，造成 CPU 资源浪费，如果液晶屏刷新的周期是 10s 更新一次，那么温湿度的数据都变化了 10 次，液晶屏才来更新数据，那拿这个产品有啥用，根本就是不准确的，所以，还是需要同步协调工作，在温湿度采集完毕之后，进行液晶屏数据的刷新，这样子，才是最准确的，并且不会浪费 CPU的资源。 

- 二值信号量在**任务与中断**同步的应用场景：

  我们在**串口接收**中，我们不知道啥时候有数据发送过来，有一个任务是做接收这些数据处理，总不能在任务中每时每刻都在任务查询有没有数据到来，那样会浪费 CPU 资源，所以在这种情况下使用二值信号量是很好的办法，当没有数据到来的时候，任务就进入阻塞态，不参与任务的调度，等到数据到来了，释放一个二值信号量，任务就立即从阻塞态中解除，进入就绪态，然后运行的时候处理数据，这样子系统的资源就会很好的被利用起来。 

  

**2、计数信号量则用于资源统计**

比如当前任务来了很多个消息，但是这些消息都放在缓冲区中，尚未处理，这时候就可以利用计数信号量对这些资源进行统计，每来一个消息就加一，每处理完一个消息就减一，这样子系统就知道有多少资源未处理的。 



## 3\. 二值信号量运作机制

创建信号量时，系统会为创建的信号量对象**分配内存**，并把**可用信号量初始化为用户自定义的个数**， 二值信号量的最大可用信号量个数为 1。

二值信号量获取：任何任务都可以从创建的二值信号量资源中获取一个二值信号量，获取成功则返回正确，否则任务会根据用户指定的**阻塞超时时间**来等待其它任务/中断释放信号量。在等待这段时间，系统将任务变成**阻塞**态，任务将被挂到该信号量的阻塞等待列表中。

- 信号量无效时候获取：在二值信号量无效的时候，假如此时有任务获取该信号量的话，那么任务将进入**阻塞**状态，如下图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200623221953.png" width="300px" /> </div>

- 中断、任务释放信号量：假如某个时间中断/任务释放了信号量，其过程具体见下图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200623221956.png" width="280px" /> </div>

- 二值信号量运作机制：由于获取无效信号量而进入阻塞态的任务将获得信号量并且恢复为就绪态，其过程具体见下图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200623221952.png" width="400px" /> </div>



## 4\. 计数信号量运作机制

计数信号量可以用于**资源管理**，**允许多个任务获取信号量访问共享资源，但会限制任务的最大数目**。**访问的任务数达到可支持的最大数目时，会阻塞其他试图获取该信号量的任务**，直到有任务释放了信号量。这就是计数型信号量的运作机制，虽然计数信号量允许多个任务访问同一个资源，但是也有限定，比如某个资源限定只能有 3 个任务访问，那么第 4 个任务访问的时候，会因为获取不到信号量而进入阻塞，等到有任务（比如任务 1）释放掉该资源的时候，第 4 个任务才能获取到信号量从而进行资源的访问，其运作的机制具体见图 21-4。 

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200623221954.png" width="600px" /> </div>



## 5\. 信号量控制块

uCOS 的信号量由多个元素组成，在信号量被创建时，需要由我们自己定义信号量控制块（也可以称之为信号量句柄），因为它是用于保存信号量的一些信息的，其数据结构OS_SEM 除了信号量必须的一些基本信息外，还有 PendList 链表与 Ctr，为的是方便系统来管理信号量。

消息队列控制块：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200623221955.png" width="200px" /> </div>

```c
struct  os_sem {                        /* Semaphore */
    /* ------------------ GENERIC  MEMBERS ------------------ */
    OS_OBJ_TYPE          Type;          /* 信号量的类型 */
    CPU_CHAR            *NamePtr;       /* 信号量的名字 */
    OS_PEND_LIST         PendList;      /* 等待信号量的任务列表 */
#if OS_CFG_DBG_EN > 0u
    OS_SEM              *DbgPrevPtr;
    OS_SEM              *DbgNextPtr;
    CPU_CHAR            *DbgNamePtr;
#endif
    /* ------------------ SPECIFIC MEMBERS ------------------ */
    OS_SEM_CTR           Ctr;			/* 可用信号量的个数，如果为 0 则表示无可用信号量 */
    CPU_TS               TS;            /* 用于记录时间戳 */
};
```



## 6\. 信号量函数接口

### 创建信号量函数OSSemCreate()

内核对象使用之前一定要先创建，这个创建过程必须要**保证在所有可能使用内核对象的任务之前**，所以一般我们都是**在创建任务之前**就创建好系统需要的内核对象（如信号量等）。

信号量创建函数源码：

```c
void  OSSemCreate (OS_SEM      *p_sem,  //多值信号量控制块指针
                   CPU_CHAR    *p_name, //多值信号量名称
                   OS_SEM_CTR   cnt,    //资源数目或事件是否发生标志
                   OS_ERR      *p_err)  //返回错误类型
{
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和定义一个局部变
                    //量，用于保存关中断前的 CPU 状态寄存器 SR（临界段关中断只需保存SR）
                    //，开中断时将该值还原。 
	
#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不继续执行
    }
#endif

#ifdef OS_SAFETY_CRITICAL_IEC61508                //如果使能（默认禁用）了安全关键
    if (OSSafetyCriticalStartFlag == DEF_TRUE) {  //如果是在调用 OSSafetyCriticalStart() 后创建该多值信号量
       *p_err = OS_ERR_ILLEGAL_CREATE_RUN_TIME;   //错误类型为“非法创建内核对象”
        return;                                   //返回，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u            //如果使能（默认使能）了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {    //如果该函数是在中断中被调用
       *p_err = OS_ERR_CREATE_ISR;                //错误类型为“在中断函数中定时”
        return;                                   //返回，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u            //如果使能（默认使能）了参数检测
    if (p_sem == (OS_SEM *)0) {       //如果参数 p_sem 为空  
       *p_err = OS_ERR_OBJ_PTR_NULL;  //错误类型为“多值信号量对象为空”
        return;                       //返回，不继续执行
    }
#endif

    OS_CRITICAL_ENTER();               //进入临界段
    p_sem->Type    = OS_OBJ_TYPE_SEM;  //初始化多值信号量指标  
    p_sem->Ctr     = cnt;                                 
    p_sem->TS      = (CPU_TS)0;
    p_sem->NamePtr = p_name;                               
    OS_PendListInit(&p_sem->PendList); //初始化该多值信号量的等待列表     

#if OS_CFG_DBG_EN > 0u       //如果使能（默认使能）了调试代码和变量 
    OS_SemDbgListAdd(p_sem); //将该定时添加到多值信号量双向调试链表
#endif
    OSSemQty++;              //多值信号量个数加1

    OS_CRITICAL_EXIT_NO_SCHED();     //退出临界段（无调度）
   *p_err = OS_ERR_NONE;             //错误类型为“无错误”
}
```

信号量创建函数使用示例：

```c
OS_SEM SemOfKey; //标志KEY1 是否被按下的信号量

/* 创建信号量 SemOfKey */
OSSemCreate((OS_SEM      *)&SemOfKey,     //指向信号量变量的指针
            (CPU_CHAR    *)"SemOfKey",    //信号量的名字
            (OS_SEM_CTR   )0,             //信号量这里是指示事件发生，所以赋值为0，表示事件还没有发生
            (OS_ERR      *)&err);         //错误类型
```



### 信号量删除函数OSSemDel()

OSSemDel() 用于删除一个信号量，信号量删除函数是根据信号量结构（信号量句柄）直接删除的，删除之后这个信号量的所有信息都会被系统清空，而且不能再次使用这个信号量了。

需要注意的是：**如果信号量没有被定义，那也是无法被删除的，如果有任务阻塞在该信号量上，尽量不要删除该信号量。**

OSSemDel() 函数源码：

```c
#if OS_CFG_SEM_DEL_EN > 0u             //如果使能了 OSSemDel() 函数 
OS_OBJ_QTY  OSSemDel (OS_SEM  *p_sem,  //多值信号量指针
                      OS_OPT   opt,    //选项
                      OS_ERR  *p_err)  //返回错误类型
{
    OS_OBJ_QTY     cnt;
    OS_OBJ_QTY     nbr_tasks;
    OS_PEND_DATA  *p_pend_data;
    OS_PEND_LIST  *p_pend_list;
    OS_TCB        *p_tcb;
    CPU_TS         ts;
    CPU_SR_ALLOC();

#ifdef OS_SAFETY_CRITICAL                      //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {                //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();        //执行安全检测异常函数
        return ((OS_OBJ_QTY)0);                //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数在中断中被调用
       *p_err = OS_ERR_DEL_ISR;                //返回错误类型为“在中断中删除”
        return ((OS_OBJ_QTY)0);                //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                    //如果使能了参数检测
    if (p_sem == (OS_SEM *)0) {               //如果 p_sem 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;          //返回错误类型为“内核对象为空”
        return ((OS_OBJ_QTY)0);               //返回0（有错误），不继续执行
    }
    switch (opt) {                            //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:              //如果选项在预期之内
        case OS_OPT_DEL_ALWAYS:
             break;                           //直接跳出

        default:                              //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;      //返回错误类型为“选项非法”
             return ((OS_OBJ_QTY)0);          //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u              //如果使能了对象类型检测
    if (p_sem->Type != OS_OBJ_TYPE_SEM) {    //如果 p_sem 不是多值信号量类型
       *p_err = OS_ERR_OBJ_TYPE;             //返回错误类型为“内核对象类型错误”
        return ((OS_OBJ_QTY)0);              //返回0（有错误），不继续执行
    }
#endif

    CPU_CRITICAL_ENTER();                      //关中断
    p_pend_list = &p_sem->PendList;            //获取信号量的等待列表到 p_pend_list
    cnt         = p_pend_list->NbrEntries;     //获取等待该信号量的任务数
    nbr_tasks   = cnt;
    switch (opt) {                             //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:               //如果只在没有任务等待的情况下删除信号量
             if (nbr_tasks == (OS_OBJ_QTY)0) { //如果没有任务在等待该信号量
#if OS_CFG_DBG_EN > 0u                         //如果使能了调试代码和变量   
                 OS_SemDbgListRemove(p_sem);   //将该信号量从信号量调试列表移除
#endif
                 OSSemQty--;                   //信号量数目减1
                 OS_SemClr(p_sem);             //清除信号量内容
                 CPU_CRITICAL_EXIT();          //开中断
                *p_err = OS_ERR_NONE;          //返回错误类型为“无错误”
             } else {                          //如果有任务在等待该信号量
                 CPU_CRITICAL_EXIT();          //开中断
                *p_err = OS_ERR_TASK_WAITING;  //返回错误类型为“有任务在等待该信号量”
             }
             break;

        case OS_OPT_DEL_ALWAYS:                             //如果必须删除信号量
             OS_CRITICAL_ENTER_CPU_EXIT();                  //锁调度器，并开中断
             ts = OS_TS_GET();                              //获取时间戳
             while (cnt > 0u) {                             //逐个移除该信号量等待列表中的任务
                 p_pend_data = p_pend_list->HeadPtr;
                 p_tcb       = p_pend_data->TCBPtr;
                 OS_PendObjDel((OS_PEND_OBJ *)((void *)p_sem),
                               p_tcb,
                               ts);
                 cnt--;
             }
#if OS_CFG_DBG_EN > 0u                                      //如果使能了调试代码和变量 
             OS_SemDbgListRemove(p_sem);                    //将该信号量从信号量调试列表移除
#endif
             OSSemQty--;                                    //信号量数目减1
             OS_SemClr(p_sem);                              //清除信号量内容
             OS_CRITICAL_EXIT_NO_SCHED();                   //减锁调度器，但不进行调度
             OSSched();                                     //任务调度，执行最高优先级的就绪任务
            *p_err = OS_ERR_NONE;                           //返回错误类型为“无错误”
             break;

        default:                                            //如果选项超出预期
             CPU_CRITICAL_EXIT();                           //开中断
            *p_err = OS_ERR_OPT_INVALID;                    //返回错误类型为“选项非法”
             break;
    }
    return ((OS_OBJ_QTY)nbr_tasks);                         //返回删除信号量前等待其的任务数
}
#endif
```

- 如果 opt 是 OS_OPT_DEL_NO_PEND，则表示只在没有任务等待的情况下删除信号量，如果当前系统中有任务阻塞在该信号量上，则不能删除，反之，则可以删除信号量。
- 如果 opt 是 OS_OPT_DEL_ALWAYS，则表示无论如何都必须删除信号量，那么在删除之前，系统会把所有阻塞在该信号量上的**任务恢复**。
- 调用 OS_PendObjDel() 函数将阻塞在内核对象（如信号量）上的任务从阻塞态恢复，此时系统再删除内核对象，删除之后，这些等待事件的任务需要被恢复。



信号量删除函数 OSSemDel() 的使用是很简单的，只需要传入要删除的信号量的句柄与选项还有保存返回的错误类型即可，调用函数时，系统将删除这个信号量。

需要注意的是：在调用删除信号量函数前，系统应存在已创建的信号量。如果删除信号量时，系统中有任务正在等待该信号量，则不应该进行删除操作，因为删除之后的信号量就不可用了。

信号量删除函数使用示例：

```c
OS_SEM  SemOfKey;                          //声明信号量 
OS_ERR      err;

/* 删除信号量 sem*/ 
OSSemDel ((OS_SEM         *)&SemOfKey,      //指向信号量的指针 
          OS_OPT_DEL_NO_PEND, 
          (OS_ERR       *)&err);            //返回错误类型
```





### 信号量释放函数OSSemPost()

与消息队列的操作一样，**信号量的释放可以在任务、中断中使用**。 

当信号量有效的时候，任务才能获取信号量，uCOS中有两个函数可使得信号量变得有效：

- 一个是在创建的时候进行初始化，将它可用的信号量个数设置一个初始值。

- 另一个是通过释放函数使得信号量变得有效。

  如果信号量用作二值信号量，那么在创建信号量的时候其初始值的范围是 0~1，假如初始值为 1 个可用的信号量的话，被获取一次就变得无效了，那就需要我们释放信号量，uCOS 提供了信号量释放函数，每调用一次该函数就释放一个信号量。

uCOS 的信号量是**允许一直释放**的，但是，**信号量的范围还需用户自己根据需求进行决定**，当用作二值信号量的时候，必须确保其可用值在 0~1 范围内；而用作计数信号量的话，其范围是由用户根据实际情况来决定的，要注意代码的严谨性。

OSSemPost() 源码：

```c
OS_SEM_CTR  OSSemPost (OS_SEM  *p_sem,    //多值信号量控制块指针
                       OS_OPT   opt,      //选项
                       OS_ERR  *p_err)    //返回错误类型
{
    OS_SEM_CTR  ctr;
    CPU_TS      ts;



#ifdef OS_SAFETY_CRITICAL                 //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {           //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();   //执行安全检测异常函数
        return ((OS_SEM_CTR)0);           //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                //如果使能（默认使能）了参数检测功能   
    if (p_sem == (OS_SEM *)0) {           //如果 p_sem 为空
       *p_err  = OS_ERR_OBJ_PTR_NULL;     //返回错误类型为“内核对象指针为空”
        return ((OS_SEM_CTR)0);           //返回0（有错误），不继续执行
    }
    switch (opt) {                                   //根据选项情况分类处理
        case OS_OPT_POST_1:                          //如果选项在预期内，不处理
        case OS_OPT_POST_ALL:
        case OS_OPT_POST_1   | OS_OPT_POST_NO_SCHED:
        case OS_OPT_POST_ALL | OS_OPT_POST_NO_SCHED:
             break;

        default:                                     //如果选项超出预期
            *p_err =  OS_ERR_OPT_INVALID;            //返回错误类型为“选项非法”
             return ((OS_SEM_CTR)0u);                //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u            //如果使能了对象类型检测           
    if (p_sem->Type != OS_OBJ_TYPE_SEM) {  //如果 p_sem 的类型不是多值信号量类型
       *p_err = OS_ERR_OBJ_TYPE;           //返回错误类型为“对象类型错误”
        return ((OS_SEM_CTR)0);            //返回0（有错误），不继续执行
    }
#endif

    ts = OS_TS_GET();                             //获取时间戳

#if OS_CFG_ISR_POST_DEFERRED_EN > 0u              //如果使能了中断延迟发布
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {    //如果该函数是在中断中被调用
        OS_IntQPost((OS_OBJ_TYPE)OS_OBJ_TYPE_SEM, //将该信号量发布到中断消息队列
                    (void      *)p_sem,
                    (void      *)0,
                    (OS_MSG_SIZE)0,
                    (OS_FLAGS   )0,
                    (OS_OPT     )opt,
                    (CPU_TS     )ts,
                    (OS_ERR    *)p_err);
        return ((OS_SEM_CTR)0);                   //返回0（尚未发布），不继续执行        
    }
#endif

    ctr = OS_SemPost(p_sem,                       //将信号量按照普通方式处理
                     opt,
                     ts,
                     p_err);

    return (ctr);                                 //返回信号的当前计数值
}
```



- 释放信号量选项 ：

```c
#define  OS_OPT_POST_FIFO (OS_OPT)(0x0000u) // 默认采用 FIFO 方式发布信号量
#define  OS_OPT_POST_LIFO (OS_OPT)(0x0010u) // uCOS 也支持采用 FIFO 方式发布信号量
#define  OS_OPT_POST_1    (OS_OPT)(0x0000u) // 发布给一个任务
#define  OS_OPT_POST_ALL  (OS_OPT)(0x0200u) // 发布给所有等待的任务，也叫广播信号量
```

- 如果使能了中断延迟发布，并且该函数在中断中被调用，则使用OS_IntQPost()函数将信号量发布到中断消息队列中。
- 使用OS_SemPost() 将信号量按照普通方式处理。

OS_SemPost() 源码：

```c
OS_SEM_CTR  OS_SemPost (OS_SEM  *p_sem, //多值信号量指针
                        OS_OPT   opt,   //选项
                        CPU_TS   ts,    //时间戳
                        OS_ERR  *p_err) //返回错误类型
{
    OS_OBJ_QTY     cnt;
    OS_SEM_CTR     ctr;
    OS_PEND_LIST  *p_pend_list;
    OS_PEND_DATA  *p_pend_data;
    OS_PEND_DATA  *p_pend_data_next;
    OS_TCB        *p_tcb;
    CPU_SR_ALLOC();



    CPU_CRITICAL_ENTER();                                   //关中断
    p_pend_list = &p_sem->PendList;                         //取出该信号量的等待列表
    if (p_pend_list->NbrEntries == (OS_OBJ_QTY)0) {         //如果没有任务在等待该信号量
        switch (sizeof(OS_SEM_CTR)) {                       //判断是否将导致该信号量计数值溢出，
            case 1u:                                        //如果溢出，则开中断，返回错误类型为
                 if (p_sem->Ctr == DEF_INT_08U_MAX_VAL) {   //“计数值溢出”，返回0（有错误），
                     CPU_CRITICAL_EXIT();                   //不继续执行。
                    *p_err = OS_ERR_SEM_OVF;
                     return ((OS_SEM_CTR)0);
                 }
                 break;

            case 2u:
                 if (p_sem->Ctr == DEF_INT_16U_MAX_VAL) {
                     CPU_CRITICAL_EXIT();
                    *p_err = OS_ERR_SEM_OVF;
                     return ((OS_SEM_CTR)0);
                 }
                 break;

            case 4u:
                 if (p_sem->Ctr == DEF_INT_32U_MAX_VAL) {
                     CPU_CRITICAL_EXIT();
                    *p_err = OS_ERR_SEM_OVF;
                     return ((OS_SEM_CTR)0);
                 }
                 break;

            default:
                 break;
        }
        p_sem->Ctr++;                                       //信号量计数值不溢出则加1
        ctr       = p_sem->Ctr;                             //获取信号量计数值到 ctr
        p_sem->TS = ts;                                     //保存时间戳
        CPU_CRITICAL_EXIT();                                //则开中断
       *p_err     = OS_ERR_NONE;                            //返回错误类型为“无错误”
        return (ctr);                                       //返回信号量的计数值，不继续执行
    }

    OS_CRITICAL_ENTER_CPU_EXIT();                           //加锁调度器，但开中断
    if ((opt & OS_OPT_POST_ALL) != (OS_OPT)0) {             //如果要将信号量发布给所有等待任务
        cnt = p_pend_list->NbrEntries;                      //获取等待任务数目到 cnt
    } else {                                                //如果要将信号量发布给优先级最高的等待任务
        cnt = (OS_OBJ_QTY)1;                                //将要操作的任务数为1，cnt 置1
    }
    p_pend_data = p_pend_list->HeadPtr;                     //获取等待列表的首个任务到 p_pend_data
    while (cnt > 0u) {                                      //逐个处理要发布的任务
        p_tcb            = p_pend_data->TCBPtr;             //取出当前任务
        p_pend_data_next = p_pend_data->NextPtr;            //取出下一个任务
        OS_Post((OS_PEND_OBJ *)((void *)p_sem),             //发布信号量给当前任务
                p_tcb,
                (void      *)0,
                (OS_MSG_SIZE)0,
                ts);
        p_pend_data = p_pend_data_next;                     //处理下一个任务          
        cnt--;
    }
    ctr = p_sem->Ctr;                                       //获取信号量计数值到 ctr
    OS_CRITICAL_EXIT_NO_SCHED();                            //减锁调度器，但不执行任务调度
    if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0) {        //如果 opt 没选择“发布时不调度任务”
        OSSched();                                          //任务调度
    }
   *p_err = OS_ERR_NONE;                                    //返回错误类型为“无错误”
    return (ctr);                                           //返回信号量的当前计数值
}
```

- 判断一下有没有任务在等待该信号量，如果没有任务在等待该信号量，则要先看看信号量的信号量计数值是否即将溢出。
- 怎么判断计数值是否溢出呢？uCOS 支持多个数据类型的信号量计数值，可以是 8 位的，16 位的，32 位的，具体是多少位是由我们自己定义的。
- 恢复任务时**将调度器锁定，但开中断**，因为接下来的操作需要操作任务与信号量的列表，系统不希望其他任务来打扰。



如果可用信号量未满，信号量控制块结构体成员变量 Ctr 就会加 1，然后判断是否有阻塞的任务，如果有的话就会恢复阻塞的任务，然后返回成功信息，用户可以选择只释放（发布）给一个任务或者是释放（发布）给所有在等待信号量的任务（广播信号量），并且**用户可以选择在释放（发布）完成的时候要不要进行任务调度，如果信号量在中断中释放，用户可以选择是否需要延迟释放（发布）**。 



OSSemPost() 使用实例：

```c
OS_SEM SemOfKey; //标志KEY1 是否被按下的信号量 
OSSemPost((OS_SEM  *)&SemOfKey,       //发布SemOfKey 
		 (OS_OPT   )OS_OPT_POST_ALL,  //发布给所有等待任务    
		 (OS_ERR *)&err); 			  //返回错误类型 
```



### 信号量获取函数OSSemPend()

与消息队列的操作一样，**信号量的获取可以在任务中使用**。 

当信号量有效的时候，任务才能获取信号量，当任务获取了某个信号量的时候，该信号量的可用个数就减 1，当它减到 0 的时候，任务就无法再获取了，并且获取的任务会进入**阻塞**态（假如用户指定了阻塞超时时间的话）。

**uCOS 支持系统中多个任务获取同一个信号量**，假如信号量中已有多个任务在等待，那么这些任务会**按照优先级顺序进行排列**，如果信号量在释放的时候选择只释放给一个任务，那么在所有等待任务中最高优先级的任务优先获得信号量，而如果信号量在释放的时候选择释放给所有任务，则所有等待的任务都会获取到信号量。

OSSemPend() 源码：

```c
OS_SEM_CTR  OSSemPend (OS_SEM   *p_sem,   //多值信号量指针
                       OS_TICK   timeout, //等待超时时间
                       OS_OPT    opt,     //选项
                       CPU_TS   *p_ts,    //等到信号量时的时间戳
                       OS_ERR   *p_err)   //返回错误类型
{
    OS_SEM_CTR    ctr;
    OS_PEND_DATA  pend_data;
    CPU_SR_ALLOC();



#ifdef OS_SAFETY_CRITICAL                       //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {                 //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();         //执行安全检测异常函数
        return ((OS_SEM_CTR)0);                 //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;                //返回错误类型为“在中断中等待”
        return ((OS_SEM_CTR)0);                 //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                     //如果使能了参数检测
    if (p_sem == (OS_SEM *)0) {                //如果 p_sem 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;           //返回错误类型为“内核对象为空”
        return ((OS_SEM_CTR)0);                //返回0（有错误），不继续执行
    }
    switch (opt) {                             //根据选项分类处理
        case OS_OPT_PEND_BLOCKING:             //如果选择“等待不到对象进行堵塞”
        case OS_OPT_PEND_NON_BLOCKING:         //如果选择“等待不到对象不进行堵塞”
             break;                            //直接跳出，不处理

        default:                               //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;       //返回错误类型为“选项非法”
             return ((OS_SEM_CTR)0);           //返回0（有错误），不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u               //如果使能了对象类型检测
    if (p_sem->Type != OS_OBJ_TYPE_SEM) {     //如果 p_sem 不是多值信号量类型
       *p_err = OS_ERR_OBJ_TYPE;              //返回错误类型为“内核对象类型错误”
        return ((OS_SEM_CTR)0);               //返回0（有错误），不继续执行
    }
#endif

    if (p_ts != (CPU_TS *)0) {                //如果 p_ts 非空
       *p_ts  = (CPU_TS)0;                    //初始化（清零）p_ts，待用于返回时间戳
    }
    CPU_CRITICAL_ENTER();                     //关中断
    if (p_sem->Ctr > (OS_SEM_CTR)0) {         //如果资源可用
        p_sem->Ctr--;                         //资源数目减1
        if (p_ts != (CPU_TS *)0) {            //如果 p_ts 非空
           *p_ts  = p_sem->TS;                //获取该信号量最后一次发布的时间戳
        }
        ctr   = p_sem->Ctr;                   //获取信号量的当前资源数目
        CPU_CRITICAL_EXIT();                  //开中断
       *p_err = OS_ERR_NONE;                  //返回错误类型为“无错误”
        return (ctr);                         //返回信号量的当前资源数目，不继续执行
    }

    if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) {    //如果没有资源可用，而且选择了不堵塞任务
        ctr   = p_sem->Ctr;                                 //获取信号量的资源数目到 ctr
        CPU_CRITICAL_EXIT();                                //开中断
       *p_err = OS_ERR_PEND_WOULD_BLOCK;                    //返回错误类型为“等待渴求堵塞”  
        return (ctr);                                       //返回信号量的当前资源数目，不继续执行
    } else {                                                //如果没有资源可用，但选择了堵塞任务
        if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) {    //如果调度器被锁
            CPU_CRITICAL_EXIT();                            //开中断
           *p_err = OS_ERR_SCHED_LOCKED;                    //返回错误类型为“调度器被锁”
            return ((OS_SEM_CTR)0);                         //返回0（有错误），不继续执行
        }
    }
                                                            
    OS_CRITICAL_ENTER_CPU_EXIT();                           //锁调度器，并重开中断
    OS_Pend(&pend_data,                                     //堵塞等待任务，将当前任务脱离就绪列表，
            (OS_PEND_OBJ *)((void *)p_sem),                 //并插入到节拍列表和等待列表。
            OS_TASK_PEND_ON_SEM,
            timeout);

    OS_CRITICAL_EXIT_NO_SCHED();                            //开调度器，但不进行调度

    OSSched();                                              //找到并调度最高优先级就绪任务
    /* 当前任务（获得信号量）得以继续运行 */
    CPU_CRITICAL_ENTER();                                   //关中断
    switch (OSTCBCurPtr->PendStatus) {                      //根据当前运行任务的等待状态分类处理
        case OS_STATUS_PEND_OK:                             //如果等待状态正常
             if (p_ts != (CPU_TS *)0) {                     //如果 p_ts 非空
                *p_ts  =  OSTCBCurPtr->TS;                  //获取信号被发布的时间戳
             }
            *p_err = OS_ERR_NONE;                           //返回错误类型为“无错误”
             break;

        case OS_STATUS_PEND_ABORT:                          //如果等待被终止中止
             if (p_ts != (CPU_TS *)0) {                     //如果 p_ts 非空
                *p_ts  =  OSTCBCurPtr->TS;                  //获取等待被中止的时间戳
             }
            *p_err = OS_ERR_PEND_ABORT;                     //返回错误类型为“等待被中止”
             break;

        case OS_STATUS_PEND_TIMEOUT:                        //如果等待超时
             if (p_ts != (CPU_TS *)0) {                     //如果 p_ts 非空
                *p_ts  = (CPU_TS  )0;                       //清零 p_ts
             }
            *p_err = OS_ERR_TIMEOUT;                        //返回错误类型为“等待超时”
             break;

        case OS_STATUS_PEND_DEL:                            //如果等待的内核对象被删除
             if (p_ts != (CPU_TS *)0) {                     //如果 p_ts 非空
                *p_ts  =  OSTCBCurPtr->TS;                  //获取内核对象被删除的时间戳
             }
            *p_err = OS_ERR_OBJ_DEL;                        //返回错误类型为“等待对象被删除”
             break;

        default:                                            //如果等待状态超出预期
            *p_err = OS_ERR_STATUS_INVALID;                 //返回错误类型为“等待状态非法”
             CPU_CRITICAL_EXIT();                           //开中断
             return ((OS_SEM_CTR)0);                        //返回0（有错误），不继续执行
    }
    ctr = p_sem->Ctr;                                       //获取信号量的当前资源数目
    CPU_CRITICAL_EXIT();                                    //开中断
    return (ctr);                                           //返回信号量的当前资源数目
}
```

**如果调度器未被锁，就锁定调度器，重新打开中断**。为什么刚刚调度器被锁就错误的呢，而现在又要锁定调度器？

那是因为**之前锁定的调度器不是被这个函数锁定的，这是不允许的，因为现在要阻塞当前任务，而调度器锁定了就表示无法进行任务调度，这也是不允许的**。那为什么又要关闭调度器呢，因为**接下来的操作是需要操作队列与任务的列表，这个时间就不会很短，系统不希望有其他任务来操作任务列表，因为可能引起其他任务解除阻塞，这可能会发生优先级翻转**。

​	比如任务 A 的优先级低于当前任务，但是在当前任务进入阻塞的过程中，任务 A 却因为其他原因解除阻塞了，那系统肯定是会	去运行任务 A，这显然是要绝对禁止的，因为挂起调度器意味着任务不能切换并且不准调用可能引起任务切换的 API 函数，所	以，锁定调度器，打开中断这样的处理，既不会影响中断的响应，又避免了其他任务来操作队列与任务的列表。 

调用 OS_Pend()函数将当前任务脱离就绪列表，并根据用户指定的阻塞时间插入到节拍列表和队列等待列表，然后打开调度器，但不进行调度。

当有任务试图获取信号量的时候，当且仅当信号量有效的时候，任务才能获取到信号量。如果信号量无效，在用户指定的阻塞超时时间中，该任务将保持阻塞状态以等待信号量有效。当其它任务或中断释放了有效的信号量，该任务将自动由阻塞态转移为就绪态。当任务等待的时间超过了指定的阻塞时间，即使信号量中还是没有可用信号量，任务也会自动从阻塞态转移为就绪态。



OSSemPend() 使用实例：

```c
OSSemPend ((OS_SEM   *)&SemOfKey,            //等待该信号量被发布 
           (OS_TICK   )0,                    //无期限等待 
           (OS_OPT    )OS_OPT_PEND_BLOCKING, //如果没有信号量可用就等待 
           (CPU_TS   *)&ts_sem_post,         //获取信号量最后一次被发布的时间戳 
           (OS_ERR   *)&err);                //返回错误类型 
```



## 7\. 使用信号量的注意事项

- **信号量访问共享资源不会导致中断延迟。当任务在执行信号量所保护的共享资源时， ISR 或高优先级任务可以抢占该任务**。 
- 应用中可以有**任意个**信号量用于保护共享资源。然而，推荐将信号量用于 I/O 端口的保护，而不是内存地址。 
- 信号量经常会被过度使用。很多情况下，访问一个简短的共享资源时不推荐使用信号量，请求和释放信号量会消耗 CPU 时间。通过关/开中断能更有效地执行这些操作。假设两个任务共享一个 32 位的整数变量。第一个任务将这个整数变量加1，第二个任务将这个变量清零。考虑到执行这些操作用时很短，不需要使用信号量。执行这个操作前任务只需关中断，执行完毕后再开中断。但是若操作浮点数变量且处理器不支持硬件浮点操作时，就需要用到信号量。因为在这种情况下处理浮点数变量需较长时间。 
- 信号量会导致一种严重的问题：**优先级反转**。 



# 互斥量

## 1\. 互斥量的基本概念

互斥量又称**互斥信号量**（本质也是一种信号量，不具备传递数据功能），是**一种特殊的二值信号量**，它和信号量不同的是，它**「支持互斥量所有权、递归访问以及防止优先级翻转」**的特性，用于**实现对临界资源的独占式处理**。

- 任意时刻互斥量的状态只有两种，**开锁或闭锁**。当互斥量被任务持有时，该互斥量处于闭锁状态，这个任务获得互斥量的所有权。当该任务释放这个互斥量时，该互斥量处于开锁状态，任务失去该互斥量的所有权。**当一个任务持有互斥量时，其他任务将不能再对该互斥量进行开锁或持有**。

- **持有该互斥量的任务也能够再次获得这个锁而不被挂起，这就是递归访问**，也就是递归互斥量的特性，这个特性与一般的信号量有很大的不同，在信号量中，由于已经不存在可用的信号量，任务递归获取信号量时会发生主动挂起任务最终形成死锁。 
- 二值信号量也可以实现临界资源的保护，但是信号量会导致的另一个潜在问题，那就是**任务优先级翻转**（具体会在下文讲解）。而 uCOS 提供的互斥量可以通过**优先级继承算法**，**降低**优先级翻转问题产生的影响，所以，用于临界资源的保护一般建议使用互斥量。 

如果想要用于实现同步（任务之间或者任务与中断之间），二值信号量或许是更好的选择，虽然互斥量也可以用于任务与任务间同步，但是互斥量更多的是用于保护资源的互锁。 



## 2\. 互斥量的优先级继承机制

在 uCOS 操作系统中为了降低优先级翻转问题利用了**优先级继承算法**。优先级继承算法是指，**「暂时提高某个占有某种资源的低优先级任务的优先级，使之与在所有等待该资源的任务中优先级最高那个任务的优先级相等，而当这个低优先级任务执行完毕释放该资源时，优先级重新回到初始设定值」**。因此，继承优先级的任务**避免了系统资源被任何中间优先级的任务抢占**。 

互斥量与二值信号量最大的不同是：**互斥量具有优先级继承机制，而信号量没有**。也就是说，某个临界资源受到一个互斥量保护，如果这个资源正在被一个低优先级任务使用，那么此时的互斥量是闭锁状态，也代表了没有任务能申请到这个互斥量，如果此时一个高优先级任务想要对这个资源进行访问，去申请这个互斥量，那么**高优先级任务会因为申请不到互斥量而进入阻塞态**，那么系统会将现在持有该互斥量的任务的优先级临时提升到与高优先级任务的优先级相同，这个**优先级提升的过程叫做优先级继承**。这个**优先级继承机制确保高优先级任务进入阻塞状态的时间尽可能短，以及将已经出现的 “优先级翻转” 危害降低到最小**。 

任务的优先级在创建的时候就已经是设置好的，高优先级的任务可以打断低优先级的任务，抢占 CPU 的使用权。但是在很多场合中，**某些资源只有一个，当低优先级任务正在占用该资源的时候，即便高优先级任务也只能乖乖的等待低优先级任务使用完该资源后释放资源**。这里「高优先级任务无法运行而低优先级任务可以运行的现象」称为 “**优先级翻转**”。 

为什么说优先级翻转在操作系统中是危害很大？因为在我们一开始创造这个系统的时候，我们就已经设置好了任务的优先级了，越重要的任务优先级越高。但是发生优先级翻转，对我们操作系统是致命的危害，**会导致系统的高优先级任务阻塞时间过长**。 



优先级翻转举例：

举个例子，现在有 3 个任务分别为 H 任务（High）、M 任务（Middle）、L 任务（Low），3 个任务的优先级顺序为 H 任务>M 任务>L 任务。正常运行的时候 H 任务可以打断 M 任务与 L 任务，M 任务可以打断 L 任务，假设系统中有一个资源被保护了，此时该资源被 L 任务正在使用中，某一刻，**H 任务需要使用该资源**，但是 L 任务还没使用完，**H任务则因为申请不到资源而进入阻塞态**，L 任务继续使用该资源，此时已经出现了“优先级翻转”现象，高优先级任务在等着低优先级的任务执行，如果在 L 任务执行的时候刚好M 任务被唤醒了，**由于 M 任务优先级比 L 任务优先级高，那么会打断 L 任务**，抢占了CPU 的使用权，**直到 M 任务执行完，再把 CUP 使用权归还给 L 任务，L 任务继续执行，等到执行完毕之后释放该资源，H 任务此时才从阻塞态解除，使用该资源**。这个过程，本来是最高优先级的 H 任务，在等待了更低优先级的 L 任务与 M 任务，其阻塞的时间是 M任务运行时间+L 任务运行时间，这只是只有 3 个任务的系统，假如很多个这样子的任务打断最低优先级的任务，那这个系统最高优先级任务岂不是崩溃了，这个现象是绝对不允许出现的，高优先级的任务必须能及时响应。所以，没有优先级继承的情况下，使用资源保护，其危害极大。

> 注意：**只有当任务想要获取被占有的资源时，才会进入阻塞态**。H任务想获取L任务占有的资源，但该资源被锁，因而H任务阻塞。而M任务不想获取L任务占有的资源，因而会打断L任务。
>

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625104258.png" width="600px" /> </div>

优先级继承举例：

若在上面的例子中，加入优先级继承机制。那么在 H 任务申请该资源的时候，由于申请不到资源会进入阻塞态，那么系统就会**把当前正在使用资源的 L 任务的优先级临时提高到与 H 任务优先级相同，此时 M 任务被唤醒了，因为它的优先级比 H 任务低，所以无法打断 L 任务**，因为此时 L 任务的优先级被临时提升到 H，所以当 L 任务使用完该资源了，进行释放，那么此时 H 任务优先级最高，将接着抢占 CPU 的使用权， H 任务的阻塞时间仅仅是 L 任务的执行时间，此时的优先级的危害降到了最低，这就是优先级继承的优势。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625104303.png" width="600px" /> </div>

注意：

在获得互斥量后，请尽快释放互斥量，同时需要注意的是**在任务持有互斥量的这段时间，不得更改任务的优先级**。UCOS 的优先级继承机制**不能解决优先级反转，只能将这种情况的影响降低到最小**，硬实时系统在一开始设计时就要避免优先级反转发生。 



## 3\. 互斥量应用场景

互斥量的使用比较单一，因为它是信号量的一种，并且它是以锁的形式存在。在初始化的时候，互斥量处于开锁的状态，而被任务持有的时候则立刻转为闭锁的状态。互斥量更适合于： 

- 可能会引起优先级翻转的情况。
- 任务可能会多次获取互斥量的情况下，这样可以避免同一任务多次递归持有而造成死锁的问题。

多任务环境下往往存在多个任务竞争同一临界资源的应用场景，互斥量可被**用于对临界资源的保护从而实现独占式访问**。另外，互斥量可以**降低**信号量存在的优先级翻转问题带来的影响。

​	比如有两个任务需要对串口进行发送数据，其硬件资源只有一个，那么两个任务肯定不能同时发送啦，不然导致数据错误，那	么，就可以用互斥量对串口资源进行保护，当一个任务正在使用串口的时候，另一个任务则无法使用串口，等到任务使用串口	完毕之后，另外一个任务才能获得串口的使用权。

另外需要注意的是**「互斥量不能在中断服务函数中使用」**，因为**其特有的优先级继承机制只在任务起作用**，而在中断的上下文环境中毫无意义。



## 4\. 互斥量运作机制

用互斥量处理不同任务对临界资源的同步访问时，任务需要获得互斥量才能进行资源访问，如果一旦有任务成功获得了互斥量，则互斥量立即变为闭锁状态，此时其他任务会因为获取不到互斥量而不能访问这个资源，任务会根据用户自定义的等待时间进行等待，直到互斥量被持有的任务释放后，其他任务才能获取互斥量从而得以访问该临界资源，此时互斥量再次上锁，如此一来就可以确保每个时刻只有一个任务正在访问这个临界资源，保证了临界资源操作的安全性。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625104306.png" width="450px" /> </div>

- 因为互斥量具有优先级继承机制，一般选择使用互斥量对资源进行保护，**如果资源被占用的时候，无论是什么优先级的任务想要使用该资源都会被阻塞**。

- 假如正在使用该资源的任务 1 比阻塞中的任务 2 的优先级还低，那么任务1 将被系统临时提升到与高优先级任务 2 相等的优先级（任务 1 的优先级从 L 变成 H）。

- 当任务 1 使用完资源之后，释放互斥量，此时任务 1 的优先级会从 H 变回原来的 L。

- 任务 2 此时可以获得互斥量，然后进行资源的访问，当任务 2 访问了资源的时候，该互斥量的状态又为闭锁状态，其他任务无法获取互斥量。



## 5\. 互斥量控制块

uCOS 的互斥量由多个元素组成，在互斥量被创建时，需要由我们自己定义互斥量（也可以称之为互斥量句柄），因为它是用于保存互斥量的一些信息的，其数据结构 OS_MUTEX 除了一些必须的基本信息外，还有指向任务控制块的指针 OwnerTCBPtr、任务优先级变量 OwnerOriginalPrio、PendList 链表与 OwnerNestingCtr 变量等，为的是方便系统来管理互斥量。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625104720.png" width="200" /> </div>

```c
struct  os_mutex {                            /* Mutual Exclusion Semaphore                             */
                                              /* ------------------ GENERIC  MEMBERS ------------------ */
    OS_OBJ_TYPE          Type;                /* 互斥量的类型，uCOS 能识别它是一个 mutex */
    CPU_CHAR            *NamePtr;             /* 互斥量的名字，每个内核对象都被分配一个名字 */
    OS_PEND_LIST         PendList;            /* 等待互斥量的任务列表 */
#if OS_CFG_DBG_EN > 0u
    OS_MUTEX            *DbgPrevPtr;
    OS_MUTEX            *DbgNextPtr;
    CPU_CHAR            *DbgNamePtr;
#endif
                                              /* ------------------ SPECIFIC MEMBERS ------------------ */
    OS_TCB              *OwnerTCBPtr;		  /* 指向持有互斥量任务控制块的指针，如果任务占用这个mutex，那么该变量会指向占用这个mutex的任务的OS_TCB */
    OS_PRIO              OwnerOriginalPrio;   /* 用于记录持有互斥量任务的优先级，如果任务占用这个mutex，那么该变量中存放着任务的原优先级，当占用mutex任务的优先级被提升时就会用到这个变量 */
    OS_NESTING_CTR       OwnerNestingCtr;     /* 表示互斥量是否可用，当该值为0的时候表示互斥量处于开锁状态，互斥量可用 */
    CPU_TS               TS;                  /* mutex 中的变量TS用于保存该mutex最后一次被释放的时间戳 */
};
```

- OwnerTCBPtr 指向持有互斥量任务控制块的指针，如果任务占用这个 mutex，那么该变量会指向占用这个 mutex 的任务的OS_TCB
- OwnerOriginalPrio 用于记录持有互斥量任务的优先级，如果任务占用这个 mutex，那么该变量中存放着任务的原优先级，当占用 mutex 任务的优先级被提升时就会用到这个变量
- OwnerNestingCtr 表示互斥量是否可用，当该值为 0 的时候表示互斥量处于开锁状态，互斥量可用
  - uCOS 允许任务递归调用同一个 mutex 多达 256 次，每递归调用一次mutex 该值就会加一，但也需要释放相同次数才能真正释放掉这个 mutex



## 6\. 互斥量函数接口

### 创建互斥量函数OSMutexCreate()

在定义完互斥量结构体变量后就可以调用 OSMutexCreate()函数进行创建一个互斥量，跟信号量的创建差不多，我们知道，其实这里的“创建互斥量”指的就是对内核对象（互斥量）的一些初始化。要特别注意的是**内核对象使用之前一定要先创建**，这个创建过程必须要保证在所有可能使用内核对象的任务之前，所以一般我们都是**在创建任务之前就创建好系统需要的内核对象（如互斥量等）**。

```c
void  OSMutexCreate (OS_MUTEX  *p_mutex, //互斥信号量指针
                     CPU_CHAR  *p_name,  //取信号量的名称
                     OS_ERR    *p_err)   //返回错误类型
{
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。 

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不继续执行
    }
#endif

#ifdef OS_SAFETY_CRITICAL_IEC61508               //如果使能（默认禁用）了安全关键
    if (OSSafetyCriticalStartFlag == DEF_TRUE) { //如果是在调用 OSSafetyCriticalStart() 后创建
       *p_err = OS_ERR_ILLEGAL_CREATE_RUN_TIME;  //错误类型为“非法创建内核对象”
        return;                                  //返回，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u           //如果使能（默认使能）了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {   //如果该函数是在中断中被调用
       *p_err = OS_ERR_CREATE_ISR;               //错误类型为“在中断函数中定时”
        return;                                  //返回，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u            //如果使能（默认使能）了参数检测
    if (p_mutex == (OS_MUTEX *)0) {   //如果参数 p_mutex 为空                       
       *p_err = OS_ERR_OBJ_PTR_NULL;  //错误类型为“创建对象为空”
        return;                       //返回，不继续执行
    }
#endif

    OS_CRITICAL_ENTER();              //进入临界段，初始化互斥信号量指标 
    p_mutex->Type              =  OS_OBJ_TYPE_MUTEX;  //标记创建对象数据结构为互斥信号量  
    p_mutex->NamePtr           =  p_name;
    p_mutex->OwnerTCBPtr       = (OS_TCB       *)0;
    p_mutex->OwnerNestingCtr   = (OS_NESTING_CTR)0;   //互斥信号量目前可用
    p_mutex->TS                = (CPU_TS        )0;
    p_mutex->OwnerOriginalPrio =  OS_CFG_PRIO_MAX;
    OS_PendListInit(&p_mutex->PendList);              //初始化该互斥信号量的等待列表   

#if OS_CFG_DBG_EN > 0u           //如果使能（默认使能）了调试代码和变量 
    OS_MutexDbgListAdd(p_mutex); //将该信号量添加到互斥信号量双向调试链表
#endif
    OSMutexQty++;                //互斥信号量个数加1         

    OS_CRITICAL_EXIT_NO_SCHED(); //退出临界段（无调度）
   *p_err = OS_ERR_NONE;          //错误类型为“无错误”
}
```

OSMutexCreate() 使用实例：

```c
OS_MUTEX mutex; //声明互斥量
/* 创建互斥量 mutex */
OSMutexCreate ((OS_MUTEX *)&mutex, //指向互斥量变量的指针
               (CPU_CHAR *)"Mutex For Test", //互斥量的名字
               (OS_ERR *)&err); //错误类型 
```



### 删除互斥量函数OSMutexDel()

OSMutexDel()用于删除一个互斥量，互斥量删除函数是根据互斥量结构（互斥量句柄）直接删除的，删除之后这个互斥量的所有信息都会被系统清空，而且不能再次使用这个互斥量了，但是需要注意的是，**如果某个互斥量没有被定义，那也是无法被删除的**，**如果有任务阻塞在该互斥量上，那么尽量不要删除该互斥量**。

```c
#if OS_CFG_MUTEX_DEL_EN > 0u                //如果使能了 OSMutexDel()   
OS_OBJ_QTY  OSMutexDel (OS_MUTEX  *p_mutex, //互斥信号量指针
                        OS_OPT     opt,     //选项
                        OS_ERR    *p_err)   //返回错误类型
{
    OS_OBJ_QTY     cnt;
    OS_OBJ_QTY     nbr_tasks;
    OS_PEND_DATA  *p_pend_data;
    OS_PEND_LIST  *p_pend_list;
    OS_TCB        *p_tcb;
    OS_TCB        *p_tcb_owner;
    CPU_TS         ts;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((OS_OBJ_QTY)0);         //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u        //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {//如果该函数在中断中被调用
       *p_err = OS_ERR_DEL_ISR;               //错误类型为“在中断中中止等待”
        return ((OS_OBJ_QTY)0);               //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                //如果使能了参数检测
    if (p_mutex == (OS_MUTEX *)0) {       //如果 p_mutex 为空             
       *p_err = OS_ERR_OBJ_PTR_NULL;      //错误类型为“对象为空”
        return ((OS_OBJ_QTY)0);           //返回0（有错误），停止执行
    }
    switch (opt) {                        //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:          //如果选项在预期内
        case OS_OPT_DEL_ALWAYS:
             break;                       //直接跳出

        default:                          //如果选项超出预期
            *p_err =  OS_ERR_OPT_INVALID; //错误类型为“选项非法”
             return ((OS_OBJ_QTY)0);      //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u               //如果使能了对象类型检测
    if (p_mutex->Type != OS_OBJ_TYPE_MUTEX) { //如果 p_mutex 非互斥信号量类型
       *p_err = OS_ERR_OBJ_TYPE;              //错误类型为“对象类型错误”
        return ((OS_OBJ_QTY)0);               //返回0（有错误），停止执行
    }
#endif

    OS_CRITICAL_ENTER();                        //进入临界段
    p_pend_list = &p_mutex->PendList;           //获取信号量的等待列表
    cnt         = p_pend_list->NbrEntries;      //获取等待该信号量的任务数
    nbr_tasks   = cnt;
    switch (opt) {                              //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:                //如果只在没任务等待时删除信号量
             if (nbr_tasks == (OS_OBJ_QTY)0) {  //如果没有任务在等待该信号量
#if OS_CFG_DBG_EN > 0u                          //如果使能了调试代码和变量  
                 OS_MutexDbgListRemove(p_mutex);//将该信号量从信号量调试列表移除
#endif
                 OSMutexQty--;                  //互斥信号量数目减1
                 OS_MutexClr(p_mutex);          //清除信号量内容
                 OS_CRITICAL_EXIT();            //退出临界段
                *p_err = OS_ERR_NONE;           //错误类型为“无错误”
             } else {                           //如果有任务在等待该信号量
                 OS_CRITICAL_EXIT();            //退出临界段
                *p_err = OS_ERR_TASK_WAITING;   //错误类型为“有任务正在等待”
             }
             break;                             //跳出

        case OS_OPT_DEL_ALWAYS:                                          //如果必须删除信号量  
             p_tcb_owner = p_mutex->OwnerTCBPtr;                         //获取信号量持有任务
             if ((p_tcb_owner       != (OS_TCB *)0) &&                   //如果持有任务存在，
                 (p_tcb_owner->Prio !=  p_mutex->OwnerOriginalPrio)) {   //而且优先级被提升过。
                 switch (p_tcb_owner->TaskState) {                       //根据其任务状态处理
                     case OS_TASK_STATE_RDY:                             //如果是就绪状态
                          OS_RdyListRemove(p_tcb_owner);                 //将任务从就绪列表移除
                          p_tcb_owner->Prio = p_mutex->OwnerOriginalPrio;//还原任务的优先级
                          OS_PrioInsert(p_tcb_owner->Prio);              //将该优先级插入优先级表格
                          OS_RdyListInsertTail(p_tcb_owner);             //将任务重插入就绪列表
                          break;                                         //跳出

                     case OS_TASK_STATE_DLY:                             //如果是延时状态
                     case OS_TASK_STATE_SUSPENDED:                       //如果是被挂起状态
                     case OS_TASK_STATE_DLY_SUSPENDED:                   //如果是延时中被挂起状态
                          p_tcb_owner->Prio = p_mutex->OwnerOriginalPrio;//还原任务的优先级
                          break;

                     case OS_TASK_STATE_PEND:                            //如果是无期限等待状态
                     case OS_TASK_STATE_PEND_TIMEOUT:                    //如果是有期限等待状态
                     case OS_TASK_STATE_PEND_SUSPENDED:                  //如果是无期等待中被挂状态
                     case OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED:          //如果是有期等待中被挂状态
                          OS_PendListChangePrio(p_tcb_owner,             //改变任务在等待列表的位置
                                                p_mutex->OwnerOriginalPrio);
                          break;

                     default:                                            //如果状态超出预期
                          OS_CRITICAL_EXIT();
                         *p_err = OS_ERR_STATE_INVALID;                  //错误类型为“任务状态非法”
                          return ((OS_OBJ_QTY)0);                        //返回0（有错误），停止执行
                 }
             }

             ts = OS_TS_GET();                                           //获取时间戳
             while (cnt > 0u) {                                          //移除该互斥信号量等待列表
                 p_pend_data = p_pend_list->HeadPtr;                     //中的所有任务。
                 p_tcb       = p_pend_data->TCBPtr;
                 OS_PendObjDel((OS_PEND_OBJ *)((void *)p_mutex),
                               p_tcb,
                               ts);
                 cnt--;
             }
#if OS_CFG_DBG_EN > 0u                          //如果使能了调试代码和变量 
             OS_MutexDbgListRemove(p_mutex);    //将信号量从互斥信号量调试列表移除
#endif
             OSMutexQty--;                      //互斥信号量数目减1
             OS_MutexClr(p_mutex);              //清除信号量内容
             OS_CRITICAL_EXIT_NO_SCHED();       //退出临界段，但不调度
             OSSched();                         //调度最高优先级任务运行
            *p_err = OS_ERR_NONE;               //错误类型为“无错误”
             break;                             //跳出

        default:                                //如果选项超出预期
             OS_CRITICAL_EXIT();                //退出临界段
            *p_err = OS_ERR_OPT_INVALID;        //错误类型为“选项非法”
             break;                             //跳出
    }
    return (nbr_tasks);                         //返回删除前信号量等待列表中的任务数
}
#endif
```

- 如果 opt 是 OS_OPT_DEL_NO_PEND，则表示只在没有任务等待的情况下删除互斥量，如果当前系统中有任务阻塞在该互斥量上，则不能删除，反之，则可以删除互斥量。 
- 如果 opt 是 OS_OPT_DEL_ALWAYS，则表示无论如何都必须删除互斥量，那么在删除之前，系统会把所有阻塞在该互斥量上的任务恢复。
- 如果任务处于就绪状态，那么就将任务从就绪列表移除，然后还原任务的优先级，互斥量控制块中的OwnerOriginalPrio 成员变量保存的就是持有互斥量任务的原本优先级。 调用 OS_PrioInsert()函数将任务按照其原本的优先级插入优先级列表中。将任务重新插入就绪列表。
- 如果任务处于延时状态、被挂起状态或者是延时中被挂起状态，就直接将任务的优先级恢复即可，并不用进行任务列表相关的操作。
- 如果任务处于无期限等待状态、有期限等待状态、无期等待中被挂状态或者是有期等待中被挂状态，那么就调用OS_PendListChangePrio() 函数改变任务在等待列表的位置，根据任务的优先级进行修改即可。
- 根据前面 cnt 记录阻塞在该互斥量上的任务个数，逐个移除该互斥量等待列表中的任务。
- 调用 OS_PendObjDel()函数将阻塞在内核对象（如互斥量）上的任务从阻塞态恢复，此时系统再删除内核对象，删除之后，这些等待事件的任务需要被恢复。



OSMutexDel()函数使用实例：

```c
OS_SEM  mutex;                              //声明互斥量 
OS_ERR      err; 
/* 删除互斥量mutex*/ 
OSMutexDel ((OS_MUTEX         *)&mutex,     //指向互斥量的指针 
			OS_OPT_DEL_NO_PEND, 
			(OS_ERR       *)&err);          //返回错误类型
```

需要注意的是在调用删除互斥量函数前，系统应存在已创建的互斥量。如果删除互斥量时，系统中有任务正在等待该互斥量，则不应该进行删除操作，因为删除之后的互斥量就不可用了。



### 获取互斥量函数OSMutexPend()

当互斥量处于开锁的状态，任务才能获取互斥量成功，当任务持有了某个互斥量的时候，其它任务就无法获取这个互斥量，需要等到持有互斥量的任务进行释放后，其他任务才能获取成功，任务通过互斥量获取函数来获取互斥量的所有权。任务对互斥量
的所有权是独占的，任意时刻互斥量只能被一个任务持有，如果互斥量处于开锁状态，那么获取该互斥量的任务将成功获得该互斥量，并拥有互斥量的使用权；如果互斥量处于闭锁状态，获取该互斥量的任务将无法获得互斥量，任务将**被挂起**，在任务被挂起之前，会进行**优先级继承**，**如果当前任务优先级比持有互斥量的任务优先级高，那么将会临时提升持有互斥量任务的优先级**。

```c
void  OSMutexPend (OS_MUTEX  *p_mutex, //互斥信号量指针
                   OS_TICK    timeout, //超时时间（节拍）
                   OS_OPT     opt,     //选项
                   CPU_TS    *p_ts,    //时间戳
                   OS_ERR    *p_err)   //返回错误类型
{
    OS_PEND_DATA  pend_data;
    OS_TCB       *p_tcb;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;               //错误类型为“在中断中等待”
        return;                                //返回，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u               //如果使能了参数检测
    if (p_mutex == (OS_MUTEX *)0) {      //如果 p_mutex 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;     //返回错误类型为“内核对象为空”
        return;                          //返回，不继续执行
    }
    switch (opt) {                       //根据选项分类处理
        case OS_OPT_PEND_BLOCKING:       //如果选项在预期内
        case OS_OPT_PEND_NON_BLOCKING:
             break;

        default:                         //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID; //错误类型为“选项非法”
             return;                     //返回，不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u               //如果使能了对象类型检测
    if (p_mutex->Type != OS_OBJ_TYPE_MUTEX) { //如果 p_mutex 非互斥信号量类型
       *p_err = OS_ERR_OBJ_TYPE;              //错误类型为“内核对象类型错误”
        return;                               //返回，不继续执行
    }
#endif

    if (p_ts != (CPU_TS *)0) {  //如果 p_ts 非空
       *p_ts  = (CPU_TS  )0;    //初始化（清零）p_ts，待用于返回时间戳    
    }

    CPU_CRITICAL_ENTER();                                //关中断
    if (p_mutex->OwnerNestingCtr == (OS_NESTING_CTR)0) { //如果信号量可用
        p_mutex->OwnerTCBPtr       =  OSTCBCurPtr;       //让当前任务持有信号量 
        p_mutex->OwnerOriginalPrio =  OSTCBCurPtr->Prio; //保存持有任务的优先级
        p_mutex->OwnerNestingCtr   = (OS_NESTING_CTR)1;  //开始嵌套
        if (p_ts != (CPU_TS *)0) {                       //如果 p_ts 非空    
           *p_ts  = p_mutex->TS;                         //返回信号量的时间戳记录
        }
        CPU_CRITICAL_EXIT();                             //开中断
       *p_err = OS_ERR_NONE;                             //错误类型为“无错误”
        return;                                          //返回，不继续执行
    }
    /* 如果信号量不可用 */
    if (OSTCBCurPtr == p_mutex->OwnerTCBPtr) { //如果当前任务已经持有该信号量
        p_mutex->OwnerNestingCtr++;            //信号量前套数加1
        if (p_ts != (CPU_TS *)0) {             //如果 p_ts 非空
           *p_ts  = p_mutex->TS;               //返回信号量的时间戳记录
        }
        CPU_CRITICAL_EXIT();                   //开中断
       *p_err = OS_ERR_MUTEX_OWNER;            //错误类型为“任务已持有信号量”
        return;                                //返回，不继续执行
    }
    /* 如果当前任务非持有该信号量 */
    if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) {//如果选择了不堵塞任务
        CPU_CRITICAL_EXIT();                            //开中断
       *p_err = OS_ERR_PEND_WOULD_BLOCK;                //错误类型为“渴求堵塞”  
        return;                                         //返回，不继续执行
    } else {                                            //如果选择了堵塞任务
        if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) {//如果调度器被锁
            CPU_CRITICAL_EXIT();                        //开中断
           *p_err = OS_ERR_SCHED_LOCKED;                //错误类型为“调度器被锁”
            return;                                     //返回，不继续执行
        }
    }
    /* 如果调度器未被锁 */                                                        
    OS_CRITICAL_ENTER_CPU_EXIT();                          //锁调度器，并重开中断
    p_tcb = p_mutex->OwnerTCBPtr;                          //获取信号量持有任务
    if (p_tcb->Prio > OSTCBCurPtr->Prio) {                 //如果持有任务优先级低于当前任务
        switch (p_tcb->TaskState) {                        //根据持有任务的任务状态分类处理
            case OS_TASK_STATE_RDY:                        //如果是就绪状态
                 OS_RdyListRemove(p_tcb);                  //从就绪列表移除持有任务
                 p_tcb->Prio = OSTCBCurPtr->Prio;          //提升持有任务的优先级到当前任务
                 OS_PrioInsert(p_tcb->Prio);               //将该优先级插入优先级表格
                 OS_RdyListInsertHead(p_tcb);              //将持有任务插入就绪列表
                 break;                                    //跳出

            case OS_TASK_STATE_DLY:                        //如果是延时状态
            case OS_TASK_STATE_DLY_SUSPENDED:              //如果是延时中被挂起状态
            case OS_TASK_STATE_SUSPENDED:                  //如果是被挂起状态
                 p_tcb->Prio = OSTCBCurPtr->Prio;          //提升持有任务的优先级到当前任务
                 break;                                    //跳出

            case OS_TASK_STATE_PEND:                       //如果是无期限等待状态
            case OS_TASK_STATE_PEND_TIMEOUT:               //如果是有期限等待状态
            case OS_TASK_STATE_PEND_SUSPENDED:             //如果是无期限等待中被挂起状态
            case OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED:     //如果是有期限等待中被挂起状态
                 OS_PendListChangePrio(p_tcb,              //改变持有任务在等待列表的位置
                                       OSTCBCurPtr->Prio);
                 break;                                    //跳出

            default:                                       //如果任务状态超出预期
                 OS_CRITICAL_EXIT();                       //开中断
                *p_err = OS_ERR_STATE_INVALID;             //错误类型为“任务状态非法”
                 return;                                   //返回，不继续执行
        }
    }
    /* 堵塞任务，将当前任务脱离就绪列表，并插入到节拍列表和等待列表。*/
    OS_Pend(&pend_data,                                     
            (OS_PEND_OBJ *)((void *)p_mutex),
             OS_TASK_PEND_ON_MUTEX,
             timeout);

    OS_CRITICAL_EXIT_NO_SCHED();          //开调度器，但不进行调度

    OSSched();                            //调度最高优先级任务运行

    CPU_CRITICAL_ENTER();                 //开中断
    switch (OSTCBCurPtr->PendStatus) {    //根据当前运行任务的等待状态分类处理
        case OS_STATUS_PEND_OK:           //如果等待正常（获得信号量）
             if (p_ts != (CPU_TS *)0) {   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS; //返回信号量最后一次被释放的时间戳
             }
            *p_err = OS_ERR_NONE;         //错误类型为“无错误”
             break;                       //跳出

        case OS_STATUS_PEND_ABORT:        //如果等待被中止
             if (p_ts != (CPU_TS *)0) {   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS; //返回等待被中止时的时间戳
             }
            *p_err = OS_ERR_PEND_ABORT;   //错误类型为“等待被中止”
             break;                       //跳出

        case OS_STATUS_PEND_TIMEOUT:      //如果超时内为获得信号量
             if (p_ts != (CPU_TS *)0) {   //如果 p_ts 非空
                *p_ts  = (CPU_TS  )0;     //清零 p_ts
             }
            *p_err = OS_ERR_TIMEOUT;      //错误类型为“超时”
             break;                       //跳出

        case OS_STATUS_PEND_DEL:          //如果信号量已被删除                  
             if (p_ts != (CPU_TS *)0) {   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS; //返回信号量被删除时的时间戳
             }
            *p_err = OS_ERR_OBJ_DEL;      //错误类型为“对象被删除”
             break;                       //跳出

        default:                           //根据等待状态超出预期
            *p_err = OS_ERR_STATUS_INVALID;//错误类型为“状态非法”
             break;                        //跳出
    }
    CPU_CRITICAL_EXIT();                   //开中断
}
```

- 如果互斥量可用，互斥量控制块中的 OwnerNestingCtr 变量为 0 则表示互斥量处于开锁状态，互斥量可用被任务获取。
- 嵌套其实是将互斥量变为闭锁状态，而其他任务就不能获取互斥量，但是本身持有互斥量的任务就拥有该互斥量的所有权，能递归获取该互斥量，每获取一次已经持有的互斥量，OwnerNestingCtr 的值就会加一，以表示互斥量嵌套，任务获取了多少次互斥量就需要释放多少次互斥量。
- 如果当前任务并没有持有该互斥量，那肯定是不能获取到的，就看看用户有没有选择阻塞任务，如果选择了不阻塞任务，那么就返回错误类型为“渴求阻塞”的错误代码，退出，不继续执行。
- 而用户如果选择了阻塞任务，就判断一下调度器是否被锁，如果调度器被锁了，就返回错误类型为“调度器被锁”的错误代码。
- 如果调度器未被锁，就锁调度器，并重开中断，原因和前面的消息队列/信号量获取函数一样。
- 获取持有互斥量的任务，判断一下当前任务与持有互斥量的任务优先级情况，如果持有互斥量的任务优先级低于当前任务，就会临时将持有互斥量任务的优先级提升，提升到与当前任务优先级一致，这就是**优先级继承**。
- 如果该任务处于就绪状态，那么从就绪列表中移除该任务，然后将该任务的优先级到与当前任务优先级一致。将该优先级插入优先级表格。再将该任务按照优先级顺序插入就绪列表。
- 如果持有互斥量任务处于延时状态、延时中被挂起状态或者是被挂起状态，仅仅是提升持有互斥量任务的优先级与当前任务优先级一致即可，不需要操作就绪列表。 
- 如果持有互斥量任务无期限等待状态、有期限等待状态、无期限等待中被挂起状态或者是有期限等待中被挂起状态，那么就直接根据任务的优先级来改变持有互斥量任务在等待列表的位置即可。 
- 调用 OS_Pend()函数阻塞任务，将当前任务脱离就绪列表，并插入到节拍列表和等待列表中。再进行一次任务调度，以运行处于最高优先级的就绪任务。



**如果任务获取互斥量成功，那么在使用完毕需要立即释放**，否则很容易造成其他任务无法获取互斥量，因为互斥量的优先级继承机制是只能将优先级危害降低，而不能完全消除。同时还需注意的是，**互斥量是不允许在中断中操作的**，因为互斥量特有的优先级继承机制在中断是毫无意义的。



OSMutexPend() 函数使用实例：

```c
OS_MUTEX mutex;                         		   //声明互斥量 
OS_ERR      err; 

OSMutexPend ((OS_MUTEX  *)&mutex,                  //申请互斥量 mutex 
             (OS_TICK    )0,                       //无期限等待 
             (OS_OPT     )OS_OPT_PEND_BLOCKING,    //如果不能申请到互斥量就堵塞任务 
             (CPU_TS    *)0,                       //不想获得时间戳 
             (OS_ERR    *)&err);                   //返回错误类 
```



### 释放互斥量函数OSMutexPost()

任务想要访问某个资源的时候，需要先获取互斥量，然后进行资源访问，**在任务使用完该资源的时候，必须要及时归还互斥量**，这样别的任务才能对资源进行访问。在前面的讲解中，我们知道，当互斥量有效的时候，任务才能获取互斥量，那么，是什么函数使得互斥量变得有效呢？uCOS 给我们提供了互斥量释放函数 OSMutexPost()，任务可以调用该函数进行释放互斥量，表示我已经用完了，别人可以申请使用，但是要注意的是，**「互斥量的释放只能在任务中，不允许在中断中释放互斥量」**。

使用该函数接口时，只有已持有互斥量所有权的任务才能释放它，当任务调用 OSMutexPost() 函数时会释放一次互斥量，当互斥量的成员变量 OwnerNestingCtr 为 0 的时候，互斥量状态才会成为开锁状态，等待获取该互斥量的任务将被唤醒。如果任务的优先级被互斥量的优先级翻转机制临时提升，那么当互斥量被完全释放后，**任务的优先级将恢复为原本设定的优先级**。

```c
void  OSMutexPost (OS_MUTEX  *p_mutex, //互斥信号量指针
                   OS_OPT     opt,     //选项
                   OS_ERR    *p_err)   //返回错误类型
{
    OS_PEND_LIST  *p_pend_list;
    OS_TCB        *p_tcb;
    CPU_TS         ts;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和定义一个局部变
                    //量，用于保存关中断前的 CPU 状态寄存器 SR（临界段关中断只需保存SR）
                    //，开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数在中断中被调用
       *p_err = OS_ERR_POST_ISR;               //错误类型为“在中断中等待”
        return;                                //返回，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                 //如果使能了参数检测
    if (p_mutex == (OS_MUTEX *)0) {        //如果 p_mutex 为空            
       *p_err = OS_ERR_OBJ_PTR_NULL;       //错误类型为“内核对象为空”
        return;                            //返回，不继续执行
    }
    switch (opt) {                         //根据选项分类处理  
        case OS_OPT_POST_NONE:             //如果选项在预期内，不处理
        case OS_OPT_POST_NO_SCHED:
             break;

        default:                           //如果选项超出预期
            *p_err =  OS_ERR_OPT_INVALID;  //错误类型为“选项非法”
             return;                       //返回，不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u               //如果使能了对象类型检测   
    if (p_mutex->Type != OS_OBJ_TYPE_MUTEX) { //如果 p_mutex 的类型不是互斥信号量类型 
       *p_err = OS_ERR_OBJ_TYPE;              //返回，不继续执行
        return;
    }
#endif

    CPU_CRITICAL_ENTER();                      //关中断
    if (OSTCBCurPtr != p_mutex->OwnerTCBPtr) { //如果当前运行任务不持有该信号量
        CPU_CRITICAL_EXIT();                   //开中断
       *p_err = OS_ERR_MUTEX_NOT_OWNER;        //错误类型为“任务不持有该信号量”
        return;                                //返回，不继续执行
    }

    OS_CRITICAL_ENTER_CPU_EXIT();                       //锁调度器，开中断
    ts          = OS_TS_GET();                          //获取时间戳
    p_mutex->TS = ts;                                   //存储信号量最后一次被释放的时间戳
    p_mutex->OwnerNestingCtr--;                         //信号量的嵌套数减1
    if (p_mutex->OwnerNestingCtr > (OS_NESTING_CTR)0) { //如果信号量仍被嵌套
        OS_CRITICAL_EXIT();                             //解锁调度器
       *p_err = OS_ERR_MUTEX_NESTING;                   //错误类型为“信号量被嵌套”
        return;                                         //返回，不继续执行
    }
    /* 如果信号量未被嵌套，已可用 */
    p_pend_list = &p_mutex->PendList;                //获取信号量的等待列表
    if (p_pend_list->NbrEntries == (OS_OBJ_QTY)0) {  //如果没有任务在等待该信号量
        p_mutex->OwnerTCBPtr     = (OS_TCB       *)0;//请空信号量持有者信息
        p_mutex->OwnerNestingCtr = (OS_NESTING_CTR)0;
        OS_CRITICAL_EXIT();                          //解锁调度器
       *p_err = OS_ERR_NONE;                         //错误类型为“无错误”
        return;                                      //返回，不继续执行
    }
    /* 如果有任务在等待该信号量 */
    if (OSTCBCurPtr->Prio != p_mutex->OwnerOriginalPrio) { //如果当前任务的优先级被改过
        OS_RdyListRemove(OSTCBCurPtr);                     //从就绪列表移除当前任务
        OSTCBCurPtr->Prio = p_mutex->OwnerOriginalPrio;    //还原当前任务的优先级
        OS_PrioInsert(OSTCBCurPtr->Prio);                  //在优先级表格插入这个优先级
        OS_RdyListInsertTail(OSTCBCurPtr);                 //将当前任务插入就绪列表尾端
        OSPrioCur         = OSTCBCurPtr->Prio;             //更改当前任务优先级变量的值
    }

    p_tcb                      = p_pend_list->HeadPtr->TCBPtr; //获取等待列表的首端任务
    p_mutex->OwnerTCBPtr       = p_tcb;                        //将信号量交给该任务
    p_mutex->OwnerOriginalPrio = p_tcb->Prio;
    p_mutex->OwnerNestingCtr   = (OS_NESTING_CTR)1;            //开始嵌套
    /* 释放信号量给该任务 */
    OS_Post((OS_PEND_OBJ *)((void *)p_mutex), 
            (OS_TCB      *)p_tcb,
            (void        *)0,
            (OS_MSG_SIZE  )0,
            (CPU_TS       )ts);

    OS_CRITICAL_EXIT_NO_SCHED();                     //减锁调度器，但不执行任务调度

    if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0) { //如果 opt 没选择“发布时不调度任务”
        OSSched();                                   //任务调度
    }

   *p_err = OS_ERR_NONE;                             //错误类型为“无错误”
}
```

- 如果互斥量仍被嵌套，也就是OwnerNestingCtr 不为 0，那还是表明当前任务还是持有互斥量的，并未完全释放，返回错误类型为“互斥量仍被嵌套”的错误代码，然后退出，不继续执行。
- 如果互斥量未被嵌套，已可用（OwnerNestingCtr 为 0），那么就获取互斥量的等待列表保存在 p_pend_list 变量中，通过该变量访问互斥量等待列表。
- 如果没有任务在等待该互斥量，那么就清空互斥量持有者信息，互斥量中的OwnerTCBPtr 成员变量重置为 0。
- 如果有任务在等待该互斥量，那么就很有可能发生了优先级继承，先看看当前任务的优先级是否被修改过，如果有则说明发生了优先级继承，就需要重新恢复任务原本的优先级。

已经获取到互斥量的任务拥有互斥量的所有权，能重复获取同一个互斥量，但是**任务获取了多少次互斥量就要释放多少次互斥量才能彻底释放掉互斥量，互斥量的状态才会变成开锁状态**，否则在此之前互斥量都处于无效状态，别的任务就无法获取该互斥量。使用该函数接口时，只有已持有互斥量所有权的任务才能释放它，每释放一次该互斥量，它的OwnerNestingCtr 成员变量就减 1。当该互斥量的 OwnerNestingCtr 成员变量为 0 时（即持有任务已经释放所有的持有操作），互斥量则变为开锁状态，等待在该互斥量上的任务将被唤醒。如果任务的优先级被互斥量的优先级翻转机制临时提升，那么当互斥量被释放后，任务的优先级将恢复为原本设定的优先级。



OSMutexPost() 使用实例：

```c
OS_MUTEX mutex; //声明互斥互斥量
OS_ERR err;
OSMutexPost ((OS_MUTEX *)&mutex, //释放互斥互斥量 mutex
    		 (OS_OPT )OS_OPT_POST_NONE, //进行任务调度
    		 (OS_ERR *)&err); //返回错误类型
```



## 7\. 总结

互斥量更适用于保护各个任务间对共享资源的互斥访问，当然系统中对于这种互斥访问的资源可以使用很多种保护的方式，如关闭中断方式、关调度器方式、信号量保护或者采用互斥量保护，但是这些方式各有好坏，下面就简单说明一下这 4 种方式的使用情况，具体见：

| 共享资源保护方式 | 说明                                                         |
| :--------------: | :----------------------------------------------------------- |
|   关闭中断方式   | 什么时候该用：**当系统能很快地结束访问该共享资源时**，如一些共享的全局变量的操作，可以关闭中断，操作完成再打开中断即可。但是我们一般不推荐使用这种方法，因为会导致中断延迟。 |
|   锁调度器方式   | **当访问共享资源较久的时候**，比如对一些列表的操作，如遍历列表、插入、删除等操作，对于操作时间是不确定的，如一些 os 中的内存分配，都可以采用锁定调度器这种方式进行共享资源的保护。 |
|  信号量保护方式  | **当该共享资源经常被多个任务使用时**可以使用这种方式。但信号量可能会导致优先级反转，并且信号量是无法解决这种危害的。 |
|  互斥量保护方式  | **推荐使用这种方法访问共享资源**，尤其当任务要访问的共享资源有阻塞时间的时候。uCOS-III 的互斥量有内置的优先级继承机制，这样**可防止优先级翻转**。然而，互斥量方式慢于信号量方式，因为互斥量需执行额外的操作，改变任务的优先级。 |



# 事件

## 1\. 事件的基本概念

事件是一种实现**任务间通信**的机制，主要用于实现**多任务间的同步**，但事件通信只能是事件类型的通信，无数据传输。**「与信号量不同的是，它可以实现一对多，多对多的同步」**。即**一个任务可以等待多个事件的发生**：可以是任意一个事件发生时唤醒任务进行事件处理；也可以是几个事件都发生后才唤醒任务进行事件处理。同样，也可以是多个任务同步多个事件。 

每一个事件组只需要很少的 RAM 空间来保存事件组的状态。事件组存储在一个 **OS_FLAGS** 类型的 Flags 变量中，该变量在事件结构体中定义。而变量的**宽度由我们自己定义**，可以是 8 位、16 位、32 位的变量，取决于 os_type.h 中的 OS_FLAGS 的位数。在STM32 中，我们一般将其定义为 32 位的变量，**有 32 个位用来实现事件标志组**。每一位代表一个事件，任务通过 “逻辑与” 或 “逻辑或” 与一个或多个事件建立关联，形成一个事件组。事件的 “逻辑或” 也被称作是**独立型同步**，指的是任务感兴趣的所有事件**任一件发生即可被唤醒**；事件 “逻辑与” 则被称为是**关联型同步**，指的是任务感兴趣的**若干事件都发生时**才被唤醒，并且事件发生的时间可以不同步。

多任务环境下，任务、中断之间往往需要同步操作，一个事件发生会告知等待中的任务，即形成一个任务与任务、中断与任务间的同步。事件可以提供一对多、多对多的同步操作。**一对多同步模型**：一个任务等待多个事件的触发，这种情况是比较常见的；**多对多同步模型**：多个任务等待多个事件的触发。任务可以通过设置事件位来实现事件的触发和等待操作。uCOS 的事件仅用于同步，不提供数据传输功能。

任务可以通过设置事件位来实现事件的触发和等待操作。uCOS 的**事件仅用于同步，不提供数据传输功能**。

uCOS 提供的事件具有如下特点：

- 事件只与任务相关联，事件相互独立，一个 32 位（数据宽度由用户定义）的事件集合用于标识该任务发生的事件类型，其中每一位表示一种事件类型（0 表示该事件类型未发生、1 表示该事件类型已经发生），一共 32 种事件类型。 

  > 我的理解：这里的事件类型指的就是事件，32位可以标识32个事件是否发生

- 事件仅用于同步，不提供数据传输功能。 

- **事件无排队性，即多次向任务设置同一事件(如果任务还未来得及读走)，等效于只设置一次**。 

- 允许多个任务对同一事件进行读写操作。 

- 支持事件等待超时机制。 

- 支持显式清除事件。 

在 uCOS 的等待事件中，用户可以选择感兴趣的事件，并且**选择等待事件的选项**，它有 4 个属性，分别是**逻辑与、逻辑或、等待所有事件清除或者等待任意事件清除**。当任务等待事件同步时，可以通过任务感兴趣的事件位和事件选项来判断当前获取的事件是否满足要求，如果满足则说明任务等待到对应的事件，系统将唤醒等待的任务；否则，任务会根据用户指定的阻塞超时时间继续等待下去。



## 2\. 事件的应用场景

uCOS 的事件用于事件类型的通讯，无数据传输，也就是说，我们**可以用事件来做标志位，判断某些事件是否发生了**，然后根据结果做处理，那很多人又会问了，为什么我不直接用变量做标志呢，岂不是更好更有效率？非也非也，若是在裸机编程中，用全局变量是最为有效的方法，这点我不否认，但是**在操作系统中，使用全局变量就要考虑以下问题**了：

- 如何对全局变量进行**保护**呢，如何处理多任务同时对它进行访问？
- 如何让内核对事件进行有效管理呢？使用全局变量的话，就需要在任务中轮询查看事件是否发送，这简直就是在**浪费 CPU 资源**啊，还有等待超时机制，使用全局变量的话需要用户自己去实现。 

所以，在操作系统中，还是使用操作系统给我们提供的通信机制就好了，简单方便还实用。 

在某些场合，可能需要多个事件发生了才能进行下一步操作，比如一些危险机器的启动，需要检查各项指标，当指标不达标的时候，无法启动，但是检查各个指标的时候，不能一下子检测完毕啊，所以，需要事件来做统一的等待，当所有的事件都完成了，那么机器才允许启动，这只是事件的其中一个应用。

事件可使用于多种场合，它**能够在一定程度上替代信号量，用于任务与任务间，中断与任务间的同步**。一个任务或中断服务例程发送一个事件给事件对象，而后等待的任务被唤醒并对相应的事件进行处理。但是它**与信号量不同的是，事件的发送操作是不可累计的，而信号量的释放动作是可累计的**。事件另外一个特性是，**接收任务可等待多种事件，即多个事件对应一个任务或多个任务**。同时按照任务等待的参数，**可选择是 “逻辑或” 触发还是 “逻辑与” 触发**。这个特性也是信号量等所不具备的，信号量只能识别单一同步动作，而不能同时等待多个事件的同步。

各个事件可分别发送或一起发送给事件对象，而任务可以等待多个事件，任务仅对感兴趣的事件进行关注。当有它们感兴趣的事件发生时并且符合感兴趣的条件，任务将被唤醒并进行后续的处理动作。



## 3\. 事件运作机制

等待（接收）事件时，可以根据感兴趣的事件类型等待事件的单个或者多个事件类型。事件等待成功后，必须使用 OS_OPT_PEND_FLAG_CONSUME 选项来清除已接收到的事件类型，否则不会清除已接收到的事件，这样就需要用户显式清除事件位。用户可以自定义通过传入  opt 选项来选择读取模式，是**等待所有感兴趣的事件**还是**等待感兴趣的任意一个事件**。

设置事件时，对指定事件写入指定的事件类型，设置事件集合的对应事件位为 1，可以一次同时写多个事件类型，设置事件成功可能会触发任务调度。清除事件时，根据参数事件句柄和待清除的事件类型，对事件对应位进行清 0 操作。事件不与任务相关联，事件相互独立，一个 32 位的变量就是事件的集合，用于标识该任务发生的事件类型，其中每一位表示一种事件类型（0 表示该事件类型未发生、1 表示该事件类型已经发生），一共 32 种事件类型（事件集合Flags（一个32 位的变量））具体见下图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625140425.png" width="600px" /> </div>

事件唤醒机制：当任务因为等待某个或者多个事件发生而进入阻塞态，当事件发生的时候会被唤醒。事件唤醒任务示意图 ：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626115658.png" width="450px" /> </div>

任务 1 对事件 3 或事件 5 感兴趣（逻辑或），当发生其中的某一个事件都会被唤醒，并且执行相应操作。而任务 2 对事件 3 与事件 5 感兴趣（逻辑与），当且仅当事件 3 与事件 5 都发生的时候，任务 2 才会被唤醒，如果只有一个其中一个事件发生，那么任务还是会继续等待事件发 生 。 如果在接收事件函数中设置了清除事件位选项 OS_OPT_PEND_FLAG_CONSUME，那么当任务唤醒后将把事件 3 和事件 5 的事件标志清零，否则事件标志将依然存在。



## 4\. 事件控制块

理论上用户可以创建任意个事件（仅限制于处理器的 RAM 大小）。通过设置 os_cfg.h 中的宏定义 OS_CFG_FLAG_EN 为 1 即可开启事件功能。事件是一个内核对象，由数据类型 **OS_FLAG_GRP**（事件标志组）定义，该数据类型由 os_flag_grp 定义（在 os.h 文件）。 

uCOS 的事件由多个元素组成，在事件被创建时，需要由我们自己定义事件（也可以称之为事件句柄），用于保存事件的一些信息，其数据结构 OS_FLAG_GRP 中除了事件必须的一些基本信息外，还有 PendList 链表与一个 32 位的事件组变量 Flags 等，为的是方便系统来管理事件。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200625140813.png" width="200px" /> </div>

```c
struct  os_flag_grp {                 /* Event Flag Group                                       */
                                      /* ------------------ GENERIC  MEMBERS ------------------ */
    OS_OBJ_TYPE          Type;        /* 事件的类型，uCOS 用于识别它是一个事件 */
    CPU_CHAR            *NamePtr;     /* 事件的名字，每个内核对象都会被分配一个名，采用字符串形式
记录下来。   */
    OS_PEND_LIST         PendList;    /* 用于控制挂起任务列表的结构体，用于记录阻塞在此事件上的任务 */
#if OS_CFG_DBG_EN > 0u
    OS_FLAG_GRP         *DbgPrevPtr;
    OS_FLAG_GRP         *DbgNextPtr;
    CPU_CHAR            *DbgNamePtr;
#endif
                                      /* ------------------ SPECIFIC MEMBERS ------------------ */
    OS_FLAGS             Flags;       /* 保存了当前事件标志位的状态。这个变量可以为8 位，16 位或 32 位 */
    CPU_TS               TS;          /* 事件中的变量 TS 用于保存该事件最后一次被释放的时间戳 */
};
```

- 因为可以有多个任务同时等待系统中的事件，所以事件中包含了一个用于控制挂起任务列表的结构体，用于记录阻塞在此事件上的任务。
- 事件中包含了很多标志位，Flags 这个变量中保存了当前这些标志位的状态。这个变量可以为8 位，16 位或 32 位。

注意：用户代码不能直接访问这个结构体，必须通过uCOS 提供的 API 访问。 



## 5\. 事件函数接口

### 事件创建函数OSFlagCreate()

事件创建函数，顾名思义，就是创建一个事件，与其他内核对象一样，都是需要先创建才能使用的资源，uCOS 给我们提供了一个创建事件的函数 OSFlagCreate()，当创建一个事件时，系统会对我们定义的事件控制块进行基本的初始化，所以，在使用创建函数之前，我们需要先定义一个事件控制块（句柄）

OSFlagCreate() 源码：

```c
void  OSFlagCreate (OS_FLAG_GRP  *p_grp,  //事件标志组指针
                    CPU_CHAR     *p_name, //命名事件标志组
                    OS_FLAGS      flags,  //标志初始值
                    OS_ERR       *p_err)  //返回错误类型
{
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，停止执行
    }
#endif

#ifdef OS_SAFETY_CRITICAL_IEC61508               //如果使能了安全关键
    if (OSSafetyCriticalStartFlag == DEF_TRUE) { //如果在调用OSSafetyCriticalStart()后创建
       *p_err = OS_ERR_ILLEGAL_CREATE_RUN_TIME;  //错误类型为“非法创建内核对象”
        return;                                  //返回，停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数是在中断中被调用
       *p_err = OS_ERR_CREATE_ISR;             //错误类型为“在中断中创建对象”
        return;                                //返回，停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u           //如果使能了参数检测
    if (p_grp == (OS_FLAG_GRP *)0) { //如果 p_grp 为空                                      
       *p_err = OS_ERR_OBJ_PTR_NULL; //错误类型为“创建对象为空”
        return;                      //返回，停止执行
    }
#endif

    OS_CRITICAL_ENTER();               //进入临界段
    p_grp->Type    = OS_OBJ_TYPE_FLAG; //标记创建对象数据结构为事件标志组
    p_grp->NamePtr = p_name;           //标记事件标志组的名称
    p_grp->Flags   = flags;            //设置标志初始值
    p_grp->TS      = (CPU_TS)0;        //清零事件标志组的时间戳
    OS_PendListInit(&p_grp->PendList); //初始化该事件标志组的等待列表  

#if OS_CFG_DBG_EN > 0u                 //如果使能了调试代码和变量
    OS_FlagDbgListAdd(p_grp);          //将该标志组添加到事件标志组双向调试链表
#endif
    OSFlagQty++;                       //事件标志组个数加1

    OS_CRITICAL_EXIT_NO_SCHED();       //退出临界段（无调度）
   *p_err = OS_ERR_NONE;               //错误类型为“无错误”
}
```



OSFlagCreate() 使用示例：

```c
OS_FLAG_GRP flag_grp;                   	    //声明事件
OS_ERR      err; 

/* 创建事件 flag_grp */ 
OSFlagCreate ((OS_FLAG_GRP  *)&flag_grp,        //指向事件的指针 
              (CPU_CHAR     *)"FLAG For Test",  //事件的名字 
              (OS_FLAGS      )0,                //事件的初始值 
              (OS_ERR       *)&err);            //返回错误类型
```



### 事件删除函数OSFlagDel()

在很多场合，某些事件只用一次的，就好比在事件应用场景说的危险机器的启动，假如各项指标都达到了，并且机器启动成功了，那这个事件之后可能就没用了，那就可以进行销毁了。uCOS 给我们提供了一个删除事件的函数——OSFlagDel()，使用它就能将事件进行删除了。当系统不再使用事件对象时，可以通过删除事件对象控制块来进行删除。

```c
#if OS_CFG_FLAG_DEL_EN > 0u                 //如果使能了 OSFlagDel() 函数
OS_OBJ_QTY  OSFlagDel (OS_FLAG_GRP  *p_grp, //事件标志组指针
                       OS_OPT        opt,   //选项
                       OS_ERR       *p_err) //返回错误类型
{
    OS_OBJ_QTY        cnt;
    OS_OBJ_QTY        nbr_tasks;
    OS_PEND_DATA     *p_pend_data;
    OS_PEND_LIST     *p_pend_list;
    OS_TCB           *p_tcb;
    CPU_TS            ts;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((OS_OBJ_QTY)0);         //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数在中断中被调用
       *p_err = OS_ERR_DEL_ISR;                //错误类型为“在中断中删除对象”
        return ((OS_OBJ_QTY)0);                //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                //如果使能了参数检测
    if (p_grp == (OS_FLAG_GRP *)0) {      //如果 p_grp 为空 
       *p_err  = OS_ERR_OBJ_PTR_NULL;     //错误类型为“对象为空”
        return ((OS_OBJ_QTY)0);           //返回0（有错误），停止执行
    }
    switch (opt) {                        //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:          //如果选项在预期内
        case OS_OPT_DEL_ALWAYS:
             break;                       //直接跳出

        default:                          //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;  //错误类型为“选项非法”
             return ((OS_OBJ_QTY)0);      //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u           //如果使能了对象类型检测
    if (p_grp->Type != OS_OBJ_TYPE_FLAG) {//如果 p_grp 不是事件标志组类型
       *p_err = OS_ERR_OBJ_TYPE;          //错误类型为“对象类型有误”
        return ((OS_OBJ_QTY)0);           //返回0（有错误），停止执行
    }
#endif
    OS_CRITICAL_ENTER();                         //进入临界段
    p_pend_list = &p_grp->PendList;              //获取消息队列的等待列表
    cnt         = p_pend_list->NbrEntries;       //获取等待该队列的任务数
    nbr_tasks   = cnt;                           //按照任务数目逐个处理
    switch (opt) {                               //根据选项分类处理
        case OS_OPT_DEL_NO_PEND:                 //如果只在没任务等待时进行删除
             if (nbr_tasks == (OS_OBJ_QTY)0) {   //如果没有任务在等待该标志组
#if OS_CFG_DBG_EN > 0u                           //如果使能了调试代码和变量
                 OS_FlagDbgListRemove(p_grp);    //将该标志组从标志组调试列表移除
#endif
                 OSFlagQty--;                    //标志组数目减1
                 OS_FlagClr(p_grp);              //清除该标志组的内容

                 OS_CRITICAL_EXIT();             //退出临界段
                *p_err = OS_ERR_NONE;            //错误类型为“无错误”
             } else {
                 OS_CRITICAL_EXIT();             //退出临界段
                *p_err = OS_ERR_TASK_WAITING;    //错误类型为“有任务在等待标志组”
             }
             break;                              //跳出

        case OS_OPT_DEL_ALWAYS:                  //如果必须删除标志组
             ts = OS_TS_GET();                   //获取时间戳
             while (cnt > 0u) {                  //逐个移除该标志组等待列表中的任务
                 p_pend_data = p_pend_list->HeadPtr;
                 p_tcb       = p_pend_data->TCBPtr;
                 OS_PendObjDel((OS_PEND_OBJ *)((void *)p_grp),
                               p_tcb,
                               ts);
                 cnt--;
             }
#if OS_CFG_DBG_EN > 0u                           //如果使能了调试代码和变量 
             OS_FlagDbgListRemove(p_grp);        //将该标志组从标志组调试列表移除
#endif
             OSFlagQty--;                        //标志组数目减1
             OS_FlagClr(p_grp);                  //清除该标志组的内容
             OS_CRITICAL_EXIT_NO_SCHED();        //退出临界段（无调度）
             OSSched();                          //调度任务
            *p_err = OS_ERR_NONE;                //错误类型为“无错误”
             break;                              //跳出

        default:                                 //如果选项超出预期
             OS_CRITICAL_EXIT();                 //退出临界段
            *p_err = OS_ERR_OPT_INVALID;         //错误类型为“选项非法”
             break;                              //跳出
    }
    return (nbr_tasks);                          //返回删除标志组前等待其的任务数
}
#endif
```

- 判断 opt 选项是否合理，该选项有两个，OS_OPT_DEL_ALWAYS 与 OS_OPT_DEL_NO_PEND
- 如果 opt 是 OS_OPT_DEL_NO_PEND，则表示只在没有任务等待的情况下删除事件，如果当前系统中有任务还在等待该事件的某些位，则不能进行删除操作，反之，则可以删除事件。
- 如果 opt 是 OS_OPT_DEL_ALWAYS，则表示无论如何都必须删除事件，那么在删除之前，系统会把所有阻塞在该事件上的任务恢复。



事件删除函数 OSFlagDel() 的使用也是很简单的，只需要传入要删除的事件的句柄与选项还有保存返回的错误类型即可，调用函数时，系统将删除这个事件。需要注意的是在 调用删除事件函数前，系统应存在已创建的事件。如果删除互斥量时，系统中有任务正在等待该事件，则不应该进行删除操作。

```c
OS_FLAG_GRP  flag_grp;                   //声明事件句柄
OS_ERR      err;
/* 删除事件 */
OSFlagDel((OS_FLAG_GRP *)& flag_grp,     //指向事件的指针
          OS_OPT_DEL_NO_PEND,
          (OS_ERR      *)&err);          //返回错误类型
```



### 事件设置函数OSFlagPost()

OSFlagPost()用于设置事件组中指定的位，当位被置位之后，并且满足任务的等待事件，那么等待在事件该标志位上的任务将会被恢复。使用该函数接口时，**通过参数指定的事件标志来设置事件的标志位，然后遍历等待在事件对象上的事件等待列表，判断是否有任务的事件激活要求与当前事件对象标志值匹配，如果有，则唤醒该任务**。简单来说，就是设置我们自己定义的事件标志位为 1，并且看看有没有任务在等待这个事件，有的话就唤醒它。

OSFlagPost() 源码：

```c
OS_FLAGS  OSFlagPost (OS_FLAG_GRP  *p_grp, //事件标志组指针
                      OS_FLAGS      flags, //选定要操作的标志位
                      OS_OPT        opt,   //选项
                      OS_ERR       *p_err) //返回错误类型
{
    OS_FLAGS  flags_cur;
    CPU_TS    ts;



#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((OS_FLAGS)0);           //返回0，停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u               //如果使能（默认使能）了参数检测
    if (p_grp == (OS_FLAG_GRP *)0) {     //如果参数 p_grp 为空 
       *p_err  = OS_ERR_OBJ_PTR_NULL;    //错误类型为“事件标志组对象为空”
        return ((OS_FLAGS)0);            //返回0，停止执行
    }
    switch (opt) {                       //根据选项分类处理
        case OS_OPT_POST_FLAG_SET:       //如果选项在预期之内
        case OS_OPT_POST_FLAG_CLR:
        case OS_OPT_POST_FLAG_SET | OS_OPT_POST_NO_SCHED:
        case OS_OPT_POST_FLAG_CLR | OS_OPT_POST_NO_SCHED:
             break;                      //直接跳出

        default:                         //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID; //错误类型为“选项非法”
             return ((OS_FLAGS)0);       //返回0，停止执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u            //如果使能了对象类型检测
    if (p_grp->Type != OS_OBJ_TYPE_FLAG) { //如果 p_grp 不是事件标志组类型
       *p_err = OS_ERR_OBJ_TYPE;           //错误类型“对象类型有误”
        return ((OS_FLAGS)0);              //返回0，停止执行
    }
#endif

    ts = OS_TS_GET();                             //获取时间戳              
#if OS_CFG_ISR_POST_DEFERRED_EN > 0u              //如果使能了中断延迟发布
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {    //如果该函数是在中断中被调用
        OS_IntQPost((OS_OBJ_TYPE)OS_OBJ_TYPE_FLAG,//将该标志组发布到中断消息队列
                    (void      *)p_grp,
                    (void      *)0,
                    (OS_MSG_SIZE)0,
                    (OS_FLAGS   )flags,
                    (OS_OPT     )opt,
                    (CPU_TS     )ts,
                    (OS_ERR    *)p_err);
        return ((OS_FLAGS)0);                     //返回0，停止执行
    }
#endif
    /* 如果没有使能中断延迟发布 */
    flags_cur = OS_FlagPost(p_grp,               //将标志组直接发布
                            flags,
                            opt,
                            ts,
                            p_err);

    return (flags_cur);                         //返回当前标志位的值
}
```

- 如果使能了中断延迟发布并且该函数在中断中被调用，则将该事件发布到中断消息队列。
- 如果没有使能中断延迟发布，则直接通过 OS_FlagPost() 函数将该事件对应的标志位置位。



OS_FlagPost() 源码：

```c
OS_FLAGS  OS_FlagPost (OS_FLAG_GRP  *p_grp, //事件标志组指针
                       OS_FLAGS      flags, //选定要操作的标志位
                       OS_OPT        opt,   //选项
                       CPU_TS        ts,    //时间戳
                       OS_ERR       *p_err) //返回错误类型
{
    OS_FLAGS        flags_cur;
    OS_FLAGS        flags_rdy;
    OS_OPT          mode;
    OS_PEND_DATA   *p_pend_data;
    OS_PEND_DATA   *p_pend_data_next;
    OS_PEND_LIST   *p_pend_list;
    OS_TCB         *p_tcb;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。 
	
    CPU_CRITICAL_ENTER();                                //关中断
    switch (opt) {                                       //根据选项分类处理
        case OS_OPT_POST_FLAG_SET:                       //如果要求将选定位置1
        case OS_OPT_POST_FLAG_SET | OS_OPT_POST_NO_SCHED:
             p_grp->Flags |=  flags;                     //将选定位置1
             break;                                      //跳出

        case OS_OPT_POST_FLAG_CLR:                       //如果要求将选定位请0
        case OS_OPT_POST_FLAG_CLR | OS_OPT_POST_NO_SCHED:
             p_grp->Flags &= ~flags;                     //将选定位请0
             break;                                      //跳出

        default:                                         //如果选项超出预期
             CPU_CRITICAL_EXIT();                        //开中断
            *p_err = OS_ERR_OPT_INVALID;                 //错误类型为“选项非法”
             return ((OS_FLAGS)0);                       //返回0，停止执行
    }
    p_grp->TS   = ts;                                    //将时间戳存入事件标志组
    p_pend_list = &p_grp->PendList;                      //获取事件标志组的等待列表
    if (p_pend_list->NbrEntries == 0u) {                 //如果没有任务在等待标志组
        CPU_CRITICAL_EXIT();                             //开中断
       *p_err = OS_ERR_NONE;                             //错误类型为“无错误”
        return (p_grp->Flags);                           //返回事件标志组的标志值
    }
    /* 如果有任务在等待标志组 */
    OS_CRITICAL_ENTER_CPU_EXIT();                     //进入临界段，重开中断
    p_pend_data = p_pend_list->HeadPtr;               //获取等待列表头个等待任务
    p_tcb       = p_pend_data->TCBPtr;
    while (p_tcb != (OS_TCB *)0) {                    //从头至尾遍历等待列表的所有任务
        p_pend_data_next = p_pend_data->NextPtr;
        mode             = p_tcb->FlagsOpt & OS_OPT_PEND_FLAG_MASK; //获取任务的标志选项
        switch (mode) {                               //根据任务的标志选项分类处理
            case OS_OPT_PEND_FLAG_SET_ALL:            //如果要求任务等待的标志位都得置1
                 flags_rdy = (OS_FLAGS)(p_grp->Flags & p_tcb->FlagsPend); 
                 if (flags_rdy == p_tcb->FlagsPend) { //如果任务等待的标志位都置1了
                     OS_FlagTaskRdy(p_tcb,            //让该任务准备运行
                                    flags_rdy,
                                    ts);
                 }
                 break;                               //跳出

            case OS_OPT_PEND_FLAG_SET_ANY:            //如果要求任务等待的标志位有1位置1即可
                 flags_rdy = (OS_FLAGS)(p_grp->Flags & p_tcb->FlagsPend);
                 if (flags_rdy != (OS_FLAGS)0) {      //如果任务等待的标志位有置1的
                     OS_FlagTaskRdy(p_tcb,            //让该任务准备运行
                                    flags_rdy,
                                    ts);
                 }
                 break;                              //跳出

#if OS_CFG_FLAG_MODE_CLR_EN > 0u                     //如果使能了标志位清0触发模式
            case OS_OPT_PEND_FLAG_CLR_ALL:           //如果要求任务等待的标志位都得请0
                 flags_rdy = (OS_FLAGS)(~p_grp->Flags & p_tcb->FlagsPend);
                 if (flags_rdy == p_tcb->FlagsPend) {//如果任务等待的标志位都请0了
                     OS_FlagTaskRdy(p_tcb,           //让该任务准备运行
                                    flags_rdy,
                                    ts);
                 }
                 break;            //跳出

            case OS_OPT_PEND_FLAG_CLR_ANY:          //如果要求任务等待的标志位有1位请0即可
                 flags_rdy = (OS_FLAGS)(~p_grp->Flags & p_tcb->FlagsPend);
                 if (flags_rdy != (OS_FLAGS)0) {    //如果任务等待的标志位有请0的
                     OS_FlagTaskRdy(p_tcb,          //让该任务准备运行
                                    flags_rdy,
                                    ts);
                 }
                 break;                            //跳出
#endif
            default:                               //如果标志选项超出预期
                 OS_CRITICAL_EXIT();               //退出临界段
                *p_err = OS_ERR_FLAG_PEND_OPT;     //错误类型为“标志选项非法”
                 return ((OS_FLAGS)0);             //返回0，停止运行
        }
        p_pend_data = p_pend_data_next;            //准备处理下一个等待任务
        if (p_pend_data != (OS_PEND_DATA *)0) {    //如果该任务存在
            p_tcb = p_pend_data->TCBPtr;           //获取该任务的任务控制块
        } else {                                   //如果该任务不存在
            p_tcb = (OS_TCB *)0;                   //清空 p_tcb，退出 while 循环
        }
    }
    OS_CRITICAL_EXIT_NO_SCHED();                  //退出临界段（无调度）

    if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0) {  //如果 opt 没选择“发布时不调度任务”
        OSSched();                                    //任务调度
    }

    CPU_CRITICAL_ENTER();        //关中断
    flags_cur = p_grp->Flags;    //获取事件标志组的标志值
    CPU_CRITICAL_EXIT();         //开中断
   *p_err     = OS_ERR_NONE;     //错误类型为“无错误”
    return (flags_cur);          //返回事件标志组的当前标志值
}
```

- 如果要求任务等待的标志位都得置 1，就获取一下任务已经等待到的事件标志，保存在 flags_rdy 变量中。
- 如果任务等待的标志位都置 1 了，就调用 OS_FlagTaskRdy() 函数让该任务恢复为就绪态，准备运行，然后跳出 switch 语句。
- 如果要求任务等待的标志位有任意一个位置1 即可。
- 如果任务等待的标志位有置 1 的，也就是满足了任务唤醒的条件，就调用 OS_FlagTaskRdy() 函数让该任务恢复为就绪态，准备运行，然后跳出 switch 语句。
- 如果任务等待的标志位都清 0 了，就调用 OS_FlagTaskRdy() 函数让该任务恢复为就绪态，准备运行，然后跳出 switch 语句。



OSFlagPost() 的使用很简单，举个例子，比如我们要记录一个事件的发生，这个事件在事件组的位置是 bit0，当它还未发生的时候，那么事件组 bit0 的值也是 0，当它发生的时候，我们往事件标志组的 bit0 位中写入这个事件，也就是 0x01，那这就表示事件已经发生了，当然，uCOS 也支持事件清零触发。为了便于理解，一般操作我们都是用宏定义来实现 #define EVENT (0x01 << x)， “<< x”表示写入事件集合的 bit x ，在使用该函数之前必须先创建事件。

OSFlagPost() 使用实例：

```c
OS_FLAG_GRP flag_grp;                   //声明事件标志组

#define KEY1_EVENT  (0x01 << 0) //设置事件掩码的位0
#define KEY2_EVENT  (0x01 << 1) //设置事件掩码的位1

static  void  AppTaskPost ( void * p_arg )
{
	OS_ERR      err;
	
	(void)p_arg;
				 
	while (DEF_TRUE) {                                                       //任务体
		if( Key_ReadStatus ( macKEY1_GPIO_PORT, macKEY1_GPIO_PIN, 1 ) == 1 ) //如果KEY1被按下
		{		                                                    		 //点亮LED1
			printf("KEY1被按下\n");
			OSFlagPost ((OS_FLAG_GRP  *)&flag_grp,                           //将标志组的BIT0置1
                  (OS_FLAGS      )KEY1_EVENT,
                  (OS_OPT        )OS_OPT_POST_FLAG_SET,
                  (OS_ERR       *)&err);
		}

		if( Key_ReadStatus ( macKEY2_GPIO_PORT, macKEY2_GPIO_PIN, 1 ) == 1 ) //如果KEY2被按下
		{		                                                    		 //点亮LED2
			printf("KEY2被按下\n");
			OSFlagPost ((OS_FLAG_GRP  *)&flag_grp,                           //将标志组的BIT1置1
                  (OS_FLAGS      )KEY2_EVENT,
                  (OS_OPT        )OS_OPT_POST_FLAG_SET,
                  (OS_ERR       *)&err);
		}

		OSTimeDlyHMSM ( 0, 0, 0, 20, OS_OPT_TIME_DLY, & err );  			 //每20ms扫描一次
	}
}
```



### 事件等待函数OSFlagPend()

既然标记了事件的发生，那么我们怎么知道他到底有没有发生，这也是需要一个函数来获取事件是否已经发生，uCOS 提供了一个等待指定事件的函数——OSFlagPend()，通过这个函数，**任务可以知道事件标志组中的哪些位，有什么事件发生了，然后通过  “逻辑与”、“逻辑或” 等操作对感兴趣的事件进行获取**，并且这个函数实现了等待超时机制，**「当且仅当任务等待的事件发生时，任务才能获取到事件信息」**。在这段时间中，如果事件一直没发生，该任务将**保持阻塞状态**以等待事件发生。当其它任务或中断服务程序往其等待的事件设置对应的标志位，该任务将自动由阻塞态转为就绪态。当任务等待的时间**超过了指定的阻塞时间，即使事件还未发生，任务也会自动从阻塞态转移为就绪态**。这样子很有效的体现了操作系统的实时性，如果事件正确获取（等待到）则返回对应的事件标志位，由用户判断再做处理，因为在事件超时的时候也可能会返回一个不能确定的事件值，所以最好判断一下任务所等待的事件是否真的发生。

OSFlagPend()源码：

```c
OS_FLAGS  OSFlagPend (OS_FLAG_GRP  *p_grp,   //事件标志组指针
                      OS_FLAGS      flags,   //选定要操作的标志位
                      OS_TICK       timeout, //等待期限（单位：时钟节拍）
                      OS_OPT        opt,     //选项
                      CPU_TS       *p_ts,    //返回等到事件标志时的时间戳
                      OS_ERR       *p_err)   //返回错误类型
{
    CPU_BOOLEAN   consume;
    OS_FLAGS      flags_rdy;
    OS_OPT        mode;
    OS_PEND_DATA  pend_data;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((OS_FLAGS)0);           //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;                //错误类型为“在中断中中止等待”
        return ((OS_FLAGS)0);                   //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u               //如果使能了参数检测
    if (p_grp == (OS_FLAG_GRP *)0) {     //如果 p_grp 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;     //错误类型为“对象为空”
        return ((OS_FLAGS)0);            //返回0（有错误），停止执行
    }
    switch (opt) {                       //根据选项分类处理
        case OS_OPT_PEND_FLAG_CLR_ALL:   //如果选项在预期内
        case OS_OPT_PEND_FLAG_CLR_ANY:
        case OS_OPT_PEND_FLAG_SET_ALL:
        case OS_OPT_PEND_FLAG_SET_ANY:
        case OS_OPT_PEND_FLAG_CLR_ALL | OS_OPT_PEND_FLAG_CONSUME:
        case OS_OPT_PEND_FLAG_CLR_ANY | OS_OPT_PEND_FLAG_CONSUME:
        case OS_OPT_PEND_FLAG_SET_ALL | OS_OPT_PEND_FLAG_CONSUME:
        case OS_OPT_PEND_FLAG_SET_ANY | OS_OPT_PEND_FLAG_CONSUME:
        case OS_OPT_PEND_FLAG_CLR_ALL | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_CLR_ANY | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_SET_ALL | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_SET_ANY | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_CLR_ALL | OS_OPT_PEND_FLAG_CONSUME | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_CLR_ANY | OS_OPT_PEND_FLAG_CONSUME | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_SET_ALL | OS_OPT_PEND_FLAG_CONSUME | OS_OPT_PEND_NON_BLOCKING:
        case OS_OPT_PEND_FLAG_SET_ANY | OS_OPT_PEND_FLAG_CONSUME | OS_OPT_PEND_NON_BLOCKING:
             break;                     //直接跳出

        default:                        //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;//错误类型为“选项非法”
             return ((OS_OBJ_QTY)0);    //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u            //如果使能了对象类型检测
    if (p_grp->Type != OS_OBJ_TYPE_FLAG) { //如果 p_grp 不是事件标志组类型 
       *p_err = OS_ERR_OBJ_TYPE;           //错误类型为“对象类型有误”
        return ((OS_FLAGS)0);              //返回0（有错误），停止执行
    }
#endif

    if ((opt & OS_OPT_PEND_FLAG_CONSUME) != (OS_OPT)0) { //选择了标志位匹配后自动取反
        consume = DEF_TRUE;
    } else {                                             //未选择标志位匹配后自动取反
        consume = DEF_FALSE;
    }

    if (p_ts != (CPU_TS *)0) {      //如果 p_ts 非空
       *p_ts = (CPU_TS)0;           //初始化（清零）p_ts，待用于返回时间戳
    }

    mode = opt & OS_OPT_PEND_FLAG_MASK;                    //从选项中提取对标志位的要求
    CPU_CRITICAL_ENTER();                                  //关中断
    switch (mode) {                                        //根据事件触发模式分类处理
        case OS_OPT_PEND_FLAG_SET_ALL:                     //如果要求所有标志位均要置1
             flags_rdy = (OS_FLAGS)(p_grp->Flags & flags); //提取想要的标志位的值
             if (flags_rdy == flags) {                     //如果该值与期望值匹配
                 if (consume == DEF_TRUE) {                //如果要求将标志位匹配后取反
                     p_grp->Flags &= ~flags_rdy;           //清0标志组的相关标志位
                 }
                 OSTCBCurPtr->FlagsRdy = flags_rdy;        //保存让任务脱离等待的标志值
                 if (p_ts != (CPU_TS *)0) {                //如果 p_ts 非空
                    *p_ts  = p_grp->TS;                    //获取任务等到标志组时的时间戳
                 }
                 CPU_CRITICAL_EXIT();                      //开中断        
                *p_err = OS_ERR_NONE;                      //错误类型为“无错误”
                 return (flags_rdy);                       //返回让任务脱离等待的标志值
             } else {                                      //如果想要标志位的值与期望值不匹配                  
                 if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) { //如果选择了不堵塞任务
                     CPU_CRITICAL_EXIT();                  //关中断
                    *p_err = OS_ERR_PEND_WOULD_BLOCK;      //错误类型为“渴求堵塞”  
                     return ((OS_FLAGS)0);                 //返回0（有错误），停止执行
                 } else {                                  //如果选择了堵塞任务
                     if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) { //如果调度器被锁
                         CPU_CRITICAL_EXIT();              //关中断
                        *p_err = OS_ERR_SCHED_LOCKED;      //错误类型为“调度器被锁”
                         return ((OS_FLAGS)0);             //返回0（有错误），停止执行
                     }
                 }
                 /* 如果调度器未被锁 */
                 OS_CRITICAL_ENTER_CPU_EXIT();             //进入临界段，重开中断           
                 OS_FlagBlock(&pend_data,                  //阻塞当前运行任务，等待事件标志组
                              p_grp,
                              flags,
                              opt,
                              timeout);
                 OS_CRITICAL_EXIT_NO_SCHED();              //退出临界段（无调度）
             }
             break;                                        //跳出

        case OS_OPT_PEND_FLAG_SET_ANY:                     //如果要求有标志位被置1即可
             flags_rdy = (OS_FLAGS)(p_grp->Flags & flags); //提取想要的标志位的值
             if (flags_rdy != (OS_FLAGS)0) {               //如果有位被置1         
                 if (consume == DEF_TRUE) {                //如果要求将标志位匹配后取反             
                     p_grp->Flags &= ~flags_rdy;           //清0湿巾标志组的相关标志位          
                 }
                 OSTCBCurPtr->FlagsRdy = flags_rdy;        //保存让任务脱离等待的标志值
                 if (p_ts != (CPU_TS *)0) {                //如果 p_ts 非空
                    *p_ts  = p_grp->TS;                    //获取任务等到标志组时的时间戳
                 }
                 CPU_CRITICAL_EXIT();                      //开中断                
                *p_err = OS_ERR_NONE;                      //错误类型为“无错误”
                 return (flags_rdy);                       //返回让任务脱离等待的标志值
             } else {                                      //如果没有位被置1                          
                 if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) { //如果没设置堵塞任务
                     CPU_CRITICAL_EXIT();                  //关中断
                    *p_err = OS_ERR_PEND_WOULD_BLOCK;      //错误类型为“渴求堵塞”     
                     return ((OS_FLAGS)0);                 //返回0（有错误），停止执行
                 } else {                                  //如果设置了堵塞任务          
                     if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) { //如果调度器被锁
                         CPU_CRITICAL_EXIT();              //关中断
                        *p_err = OS_ERR_SCHED_LOCKED;      //错误类型为“调度器被锁”
                         return ((OS_FLAGS)0);             //返回0（有错误），停止执行
                     }
                 }
                 /* 如果调度器没被锁 */                                    
                 OS_CRITICAL_ENTER_CPU_EXIT();             //进入临界段，重开中断             
                 OS_FlagBlock(&pend_data,                  //阻塞当前运行任务，等待事件标志组
                              p_grp,
                              flags,
                              opt,
                              timeout);
                 OS_CRITICAL_EXIT_NO_SCHED();              //退出中断（无调度）
             }
             break;                                        //跳出

#if OS_CFG_FLAG_MODE_CLR_EN > 0u                           //如果使能了标志位清0触发模式
        case OS_OPT_PEND_FLAG_CLR_ALL:                     //如果要求所有标志位均要清0
             flags_rdy = (OS_FLAGS)(~p_grp->Flags & flags);//提取想要的标志位的值
             if (flags_rdy == flags) {                     //如果该值与期望值匹配
                 if (consume == DEF_TRUE) {                //如果要求将标志位匹配后清0
                     p_grp->Flags |= flags_rdy;            //置1标志组的相关标志位
                 }
                 OSTCBCurPtr->FlagsRdy = flags_rdy;        //保存让任务脱离等待的标志值
                 if (p_ts != (CPU_TS *)0) {                //如果 p_ts 非空
                    *p_ts  = p_grp->TS;                    //获取任务等到标志组时的时间戳
                 }
                 CPU_CRITICAL_EXIT();                      //开中断
                *p_err = OS_ERR_NONE;                      //错误类型为“无错误”
                 return (flags_rdy);                       //返回0（有错误），停止执行
             } else {                                      //如果想要标志位的值与期望值不匹配
                 if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) {  //如果选择了不堵塞任务
                     CPU_CRITICAL_EXIT();                  //关中断
                    *p_err = OS_ERR_PEND_WOULD_BLOCK;      //错误类型为“渴求堵塞”
                     return ((OS_FLAGS)0);                 //返回0（有错误），停止执行
                 } else {                                  //如果选择了堵塞任务
                     if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) { //如果调度器被锁
                         CPU_CRITICAL_EXIT();              //关中断           
                        *p_err = OS_ERR_SCHED_LOCKED;      //错误类型为“调度器被锁”
                         return ((OS_FLAGS)0);             //返回0（有错误），停止执行
                     }
                 }
                 /* 如果调度器未被锁 */                                          
                 OS_CRITICAL_ENTER_CPU_EXIT();             //进入临界段，重开中断      
                 OS_FlagBlock(&pend_data,                  //阻塞当前运行任务，等待事件标志组
                              p_grp,
                              flags,
                              opt,
                              timeout);
                 OS_CRITICAL_EXIT_NO_SCHED();             //退出临界段（无调度）
             }
             break;                                       //跳出

        case OS_OPT_PEND_FLAG_CLR_ANY:                    //如果要求有标志位被清0即可
             flags_rdy = (OS_FLAGS)(~p_grp->Flags & flags);//提取想要的标志位的值
             if (flags_rdy != (OS_FLAGS)0) {              //如果有位被清0
                 if (consume == DEF_TRUE) {               //如果要求将标志位匹配后取反 
                     p_grp->Flags |= flags_rdy;           //置1湿巾标志组的相关标志位  
                 }
                 OSTCBCurPtr->FlagsRdy = flags_rdy;       //保存让任务脱离等待的标志值 
                 if (p_ts != (CPU_TS *)0) {               //如果 p_ts 非空
                    *p_ts  = p_grp->TS;                   //获取任务等到标志组时的时间戳
                 }
                 CPU_CRITICAL_EXIT();                     //开中断 
                *p_err = OS_ERR_NONE;                     //错误类型为“无错误”
                 return (flags_rdy);                      //返回0（有错误），停止执行
             } else {                                     //如果没有位被清0
                 if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) { //如果没设置堵塞任务
                     CPU_CRITICAL_EXIT();                 //开中断
                    *p_err = OS_ERR_PEND_WOULD_BLOCK;     //错误类型为“渴求堵塞”
                     return ((OS_FLAGS)0);                //返回0（有错误），停止执行
                 } else {                                 //如果设置了堵塞任务  
                     if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) { //如果调度器被锁
                         CPU_CRITICAL_EXIT();             //开中断
                        *p_err = OS_ERR_SCHED_LOCKED;     //错误类型为“调度器被锁”
                         return ((OS_FLAGS)0);            //返回0（有错误），停止执行
                     }
                 }
                 /* 如果调度器没被锁 */                                          
                 OS_CRITICAL_ENTER_CPU_EXIT();            //进入临界段，重开中断
                 OS_FlagBlock(&pend_data,                 //阻塞当前运行任务，等待事件标志组
                              p_grp,
                              flags,
                              opt,
                              timeout);
                 OS_CRITICAL_EXIT_NO_SCHED();             //退出中断（无调度）
             }
             break;                                       //跳出
#endif

        default:                                          //如果要求超出预期
             CPU_CRITICAL_EXIT();
            *p_err = OS_ERR_OPT_INVALID;                  //错误类型为“选项非法”
             return ((OS_FLAGS)0);                        //返回0（有错误），停止执行
    }

    OSSched();                                            //任务调度
    /* 任务等到了事件标志组后得以继续运行 */
    CPU_CRITICAL_ENTER();                                 //关中断
    switch (OSTCBCurPtr->PendStatus) {                    //根据运行任务的等待状态分类处理
        case OS_STATUS_PEND_OK:                           //如果等到了事件标志组
             if (p_ts != (CPU_TS *)0) {                   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS;                 //返回等到标志组时的时间戳
             }
            *p_err = OS_ERR_NONE;                         //错误类型为“无错误”
             break;                                       //跳出

        case OS_STATUS_PEND_ABORT:                        //如果等待被中止
             if (p_ts != (CPU_TS *)0) {                   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS;                 //返回等待被中止时的时间戳
             }
             CPU_CRITICAL_EXIT();                         //开中断
            *p_err = OS_ERR_PEND_ABORT;                   //错误类型为“等待被中止”
             break;                                       //跳出

        case OS_STATUS_PEND_TIMEOUT:                      //如果等待超时
             if (p_ts != (CPU_TS *)0) {                   //如果 p_ts 非空
                *p_ts  = (CPU_TS  )0;                     //清零 p_ts
             }
             CPU_CRITICAL_EXIT();                         //开中断
            *p_err = OS_ERR_TIMEOUT;                      //错误类型为“超时”
             break;                                       //跳出

        case OS_STATUS_PEND_DEL:                          //如果等待对象被删除
             if (p_ts != (CPU_TS *)0) {                   //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS;                 //返回对象被删时的时间戳
             }
             CPU_CRITICAL_EXIT();                         //开中断
            *p_err = OS_ERR_OBJ_DEL;                      //错误类型为“对象被删”
             break;                                       //跳出

        default:                                          //如果等待状态超出预期
             CPU_CRITICAL_EXIT();                         //开中断
            *p_err = OS_ERR_STATUS_INVALID;               //错误类型为“状态非法”
             break;                                       //跳出
    }
    if (*p_err != OS_ERR_NONE) {                          //如果有错误存在
        return ((OS_FLAGS)0);                             //返回0（有错误），停止执行
    }
    /* 如果没有错误存在 */
    flags_rdy = OSTCBCurPtr->FlagsRdy;                    //读取让任务脱离等待的标志值
    if (consume == DEF_TRUE) {                            //如果需要取反触发事件的标志位
        switch (mode) {                                   //根据事件触发模式分类处理
            case OS_OPT_PEND_FLAG_SET_ALL:                //如果是通过置1来标志事件的发生
            case OS_OPT_PEND_FLAG_SET_ANY:                                           
                 p_grp->Flags &= ~flags_rdy;              //清0标志组里触发事件的标志位
                 break;                                   //跳出

#if OS_CFG_FLAG_MODE_CLR_EN > 0u                          //如果使能了标志位清0触发模式
            case OS_OPT_PEND_FLAG_CLR_ALL:                //如果是通过清0来标志事件的发生
            case OS_OPT_PEND_FLAG_CLR_ANY:                 
                 p_grp->Flags |=  flags_rdy;              //置1标志组里触发事件的标志位
                 break;                                   //跳出
#endif
            default:                                      //如果触发模式超出预期
                 CPU_CRITICAL_EXIT();                     //开中断
                *p_err = OS_ERR_OPT_INVALID;              //错误类型为“选项非法”
                 return ((OS_FLAGS)0);                    //返回0（有错误），停止执行
        }
    }
    CPU_CRITICAL_EXIT();                                  //开中断
   *p_err = OS_ERR_NONE;                                  //错误类型为“无错误”
    return (flags_rdy);                                   //返回让任务脱离等待的标志值
}
```

- uCOS 利用**状态机**的方法等待事件，根据不一样的情况分别进行处理。
  - 处理过程：当用户调用这个函数接口时，**系统首先根据用户指定参数和接收选项来判断它要等待的事件是否发生，如果已经发生，则根据等待选项来决定是否清除事件的相应标志位，并且返回事件标志位的值**，但是这个值可能不是一个稳定的值，所以在等待到对应事件的时候，我们最好要判断事件是否与任务需要的一致；**如果事件没有发生，则把任务添加到事件等待列表中，将当前任务阻塞**，直到事件发生或等待时间超时。

```c
OS_FLAG_GRP flag_grp;           //声明事件标志组

#define KEY1_EVENT  (0x01 << 0)	//设置事件掩码的位0
#define KEY2_EVENT  (0x01 << 1)	//设置事件掩码的位1

static  void  AppTaskPend ( void * p_arg )
{
	OS_ERR      err;
  	OS_FLAGS      flags_rdy;
	
	(void)p_arg;
					 
	while (DEF_TRUE) { //任务体
        //等待标志组的的BIT0和BIT1均被置1 
        flags_rdy =   OSFlagPend ((OS_FLAG_GRP *)&flag_grp,                 
                                  (OS_FLAGS     )( KEY1_EVENT | KEY2_EVENT ),
                                  (OS_TICK      )0,
                                  (OS_OPT       )OS_OPT_PEND_FLAG_SET_ALL |
                                  OS_OPT_PEND_BLOCKING |
                                  OS_OPT_PEND_FLAG_CONSUME,
                                  (CPU_TS      *)0,
                                  (OS_ERR      *)&err);
                                  
        if((flags_rdy & (KEY1_EVENT|KEY2_EVENT)) == (KEY1_EVENT|KEY2_EVENT))
        {
          /* 如果接收完成并且正确 */
          printf ( "KEY1与KEY2都按下\n");	
          macLED1_TOGGLE(); //LED1反转
        }                         
	}
}
```



# 软件定时器

## 1. 软件定时器的基本概念

**定时器，是指从指定的时刻开始，经过一个指定时间，然后触发一个超时事件，用户可以自定义定时器的周期与频率**。

定时器有硬件定时器和软件定时器之分：

- 硬件定时器是芯片本身提供的定时功能。一般是由外部晶振提供给芯片输入时钟，芯片向软件模块提供一组配置寄存器，接受控制输入，到达设定时间值后芯片中断控制器产生时钟中断。硬件定时器的精度一般很高，可以达到纳秒级别，并且是中断触发方式。 
- 软件定时器，软件定时器是由操作系统提供的一类系统接口，它**构建在硬件定时器基础之上**，使系统能够提供不受硬件定时器资源限制的定时器服务，它实现的功能与硬件定时器也是类似的。

使用硬件定时器时，每次在定时时间到达之后就会自动触发一个中断，用户在中断中处理信息；而使用软件定时器时，需要我们在创建软件定时器时指定时间到达后要调用的函数（回调函数），**在回调函数中处理信息**。 注意：软件定时器回调函数的**上下文是任务**。

软件定时器在被创建之后，当经过设定的时钟计数值后会触发用户定义的回调函数。**定时精度与系统时钟的周期有关**。一般系统利用 SysTick 作为软件定时器的基础时钟，软件定时器的回调函数类似硬件的中断服务函数，所以，**回调函数也要快进快出**，而且回调函数中**不能有任何阻塞任务运行的情况**（软件定时器回调函数的上下文环境是任务），比如 OSTimeDly()以及其它能阻塞任务运行的函数，两次触发回调函数的时间间隔 period 叫定时器的定时周期。

uCOS 操作系统提供软件定时器功能，软件定时器的使用相当于**扩展了定时器的数量**，允许创建更多的定时业务。

uCOS 提供的软件定时器支持**单次模式和周期模式**，单次模式和周期模式的定时时间到之后都会调用软件定时器的回调函数，用户可以在回调函数中加入要执行的工程代码。 

- 单次模式：当用户创建了定时器并启动了定时器后，定时时间到了，只执行一次回调函数之后就将不再重复执行，当然用户还是可以调用软件定时器启动函数 OSTmrStart() 来启动一次软件定时器。 
- 周期模式：这个定时器会按照设置的定时时间循环执行回调函数，直到用户将定时器删除。 

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626102733.png" width="600px" /> </div>

当然，uCOS 中软件定时器的周期模式也分为两种，一种是**有初始化延迟的周期模式**，另一种是**无初始化延迟的周期模式**，由 OSTmrCreate()中的“dly”参数设置，这两种周期模式基本是一致的，但是有个细微的差别。 

- 有初始化延迟的周期模式：在软件定时器创建的时候，其第一个定时周期是由定时器中的 dly 参数决定，然后在运行完第一个周期后，其以后的定时周期均由 period 参数决定。
- 无初始化延迟的周期模式：该定时器从始至终都按照周期运行。

比如我们创建两个周期定时器，定时器 1 是无初始化延迟的定时器，周期为 100 个tick（时钟节拍），定时器 2 是有初始化延迟的定时器，其初始化延迟的 dly 参数为 150 个tick，周期为 100 个 tick，从 tick 为 0 的时刻就启动了两个软件定时器。定时器 1 从始至终都按照正常的周期运行，但是定时器 2 则在第一个周期中的运行周期为 dly，从第二个运行周期开始按照正常的100 个tick 来运行。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626102933.png" width="600px" /> </div>

uCOS 通过一个 **OS_TmrTask** 任务（也叫软件定时器任务）来管理软定时器，它是在**系统初始化时（OSInit()函数中）自动创建**的，为了满足用户定时需求。TmrTask 任务会在定时器节拍到来的时候检查定时器列表，看看是否有定时器时间到了，如果到了就调用其回调函数。



## 2. 软件定时器的应用场景

在很多应用中，我们需要一些定时器任务，硬件定时器受硬件的限制，**数量上不足以满足用户的实际需求**，无法提供更多的定时器，那么可以采用软件定时器来完成，由软件定时器代替硬件定时器任务。但需要注意的是**软件定时器的精度是无法和硬件定时器相比的**，因为**在软件定时器的定时过程中是极有可能被其它中断所打断，因为软件定时器的执行上下文环境是任务**。所以，软件定时器更适用于对时间精度要求不高的任务，一些辅助型的任务。



## 3. 软件定时器的精度

在操作系统中，通常软件定时器**以系统节拍为计时的时基单位**。系统节拍是系统的心跳节拍，表示系统时钟的频率，就类似人的心跳，1s 能跳动多少下，系统节拍配置为OS_CFG_TICK_RATE_HZ，该宏在 os_app_cfg.h 中有定义，默认是 1000。那么系统的时钟节拍周期就为 1ms（1s 跳动 1000 下，每一下就为 1ms）。 
uCOS 软件定时器的精度（分辨率）**决定于系统时基频率**，也就是变量OS_CFG_TMR_TASK_RATE_HZ 的值，它是以 Hz 为单位的。**如果软件定时器任务的频率（OS_CFG_TMR_TASK_RATE_HZ）设置为 10Hz，系统中所有软件定时器的精度为十分之一秒**。事实上，这是用于软件定时器的推荐值，因为软件定时器常用于不精确时间尺度的任务。 

而且**定时器所定时的数值必须是这个定时器任务精度的整数倍**，例如，定时器任务的频率为 10HZ，那么上层软件定时器定时数值只能是 100ms，200ms，1000ms 等，而不能取值为 150ms。由于系统节拍与软件定时器频率决定了系统中定时器能够分辨的精确度，用户可以根据实际 CPU 的处理能力和实时性需求设置合适的数值，软件定时器频率的值越大，精度越高，但是系统开销也将越大，因为这代表在 1 秒中系统进入定时器任务的次数也就越多。 

注意：定时器任务的频率 OS_CFG_TMR_TASK_RATE_HZ 的值不能大于系统时基频率 OS_CFG_TMR_TASK_RATE_HZ 的值。 



## 4. 软件定时器控制块

uCOS 的软件定时器也属于内核对象，是一个可以裁剪的功能模块，同样在系统中由一个控制块管理其相关信息，软件定时器的控制块中包含创建的软件定时器基本信息，在使用定时器前我们需要通过 OSTmrCreate()函数创建一个软件定时器，但是在创建前需要我们定义一个定时器的句柄（控制块）。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626104359.png" width="200px" /> </div>

```c
struct  os_tmr {
    OS_OBJ_TYPE          Type;			  /* 内核对象类型 */
    CPU_CHAR            *NamePtr;         /* 指向内核对象名的指针 */
    OS_TMR_CALLBACK_PTR  CallbackPtr;     /* 指向函数的指针，被指向的函数称作回调函数 */
    void                *CallbackPtrArg;  /* 指向回调函数中的形参 */
    OS_TMR              *NextPtr;         /* 指向下一个定时器 */
    OS_TMR              *PrevPtr;		  /* 指向前一个定时器 */
    OS_TICK              Match;           /* 匹配时间（唤醒时间） */
    OS_TICK              Remain;          /* 距定时器定时时间到达还有多少个时基 */
    OS_TICK              Dly;             /* 定时器的初次定时值 */
    OS_TICK              Period;          /* 定时器的定时周期 */
    OS_OPT               Opt;             /* 定时器的选项 */
    OS_STATE             State;     	  /* 定时器的状态 */
#if OS_CFG_DBG_EN > 0u
    OS_TMR              *DbgPrevPtr;
    OS_TMR              *DbgNextPtr;
#endif
};
```

- CallbackPtr 是一个指向函数的指针，被指向的函数称作回调函数， 当定时器定时时间到达后，其指向的回调函数将被调用。如果定时器创建时该指针值为NULL，回调函数将不会被调用。 
- 当回调函数需要接受一个参数时 （CallbackPtr 不为 NULL），这个参数通过 CallbackPtrArg 指针传递给回调函数，简单来说就是指向回调函数中的形参。
- NextPtr 与 PrevPtr 联合工作将定时器链接成一个双向链表。
- 当定时器管理器中的变量 OSTmrTickCtr 的值等于定时器中的Match 值时，表示定时器时间到了，Match 也被称为匹配时间（唤醒时间）。
- Remain 中保存了距定时器定时时间到达还有多少个时基。
- Dly 为定时器的初次定时值（可以看作是第一次延迟的值），这个值以定时器时基为最小单位。
- Period 是定时器的定时周期（当被设置为周期模式时）。这个值以定时器时基为最小单位。 
- Opt 是定时器的选项，可选参数。



## 5. 软件定时器函数接口

### 创建软件定时器函数OSTmrCreate()

软件定时器也是内核对象，与消息队列、信号量等内核对象一样，都是需要创建之后才能使用的资源，我们在创建的时候需要指定定时器延时初始值 dly、定时器周期、定时器工作模式、回调函数等。每个软件定时器只需少许的 RAM 空间，理论上 uCOS 支持无限多个软件定时器，只要 RAM 足够即可。 

```c
void  OSTmrCreate (OS_TMR               *p_tmr,          //定时器控制块指针
                   CPU_CHAR             *p_name,         //命名定时器，有助于调试
                   OS_TICK               dly,            //初始定时节拍数
                   OS_TICK               period,         //周期定时重载节拍数
                   OS_OPT                opt,            //选项
                   OS_TMR_CALLBACK_PTR   p_callback,     //定时到期时的回调函数
                   void                 *p_callback_arg, //传给回调函数的参数
                   OS_ERR               *p_err)          //返回错误类型
{
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和定义一个局部变
                    //量，用于保存关中断前的 CPU 状态寄存器 SR（临界段关中断只需保存SR）
                    //，开中断时将该值还原。 

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不执行定时操作
    }
#endif

#ifdef OS_SAFETY_CRITICAL_IEC61508               //如果使能（默认禁用）了安全关键
    if (OSSafetyCriticalStartFlag == DEF_TRUE) { //如果是在调用 OSSafetyCriticalStart() 后创建该定时器
       *p_err = OS_ERR_ILLEGAL_CREATE_RUN_TIME;  //错误类型为“非法创建内核对象”
        return;                                  //返回，不执行定时操作
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能（默认使能）了中断中非法调用检测  
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数是在中断中被调用
       *p_err = OS_ERR_TMR_ISR;                 //错误类型为“在中断函数中定时”
        return;                                 //返回，不执行定时操作
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                          //如果使能（默认使能）了参数检测
    if (p_tmr == (OS_TMR *)0) {                     //如果参数 p_tmr 为空
       *p_err = OS_ERR_OBJ_PTR_NULL;                //错误类型为“定时器对象为空”
        return;                                     //返回，不执行定时操作
    }

    switch (opt) {                                  //根据延时选项参数 opt 分类操作
        case OS_OPT_TMR_PERIODIC:                   //如果选择周期性定时
             if (period == (OS_TICK)0) {            //如果周期重载实参为0
                *p_err = OS_ERR_TMR_INVALID_PERIOD; //错误类型为“周期重载实参无效”
                 return;                            //返回，不执行定时操作
             }
             break;

        case OS_OPT_TMR_ONE_SHOT:                   //如果选择一次性定时
             if (dly == (OS_TICK)0) {               //如果定时初始实参为0
                *p_err = OS_ERR_TMR_INVALID_DLY;    //错误类型为“定时初始实参无效”
                 return;                            //返回，不执行定时操作
             }
             break;

        default:                                    //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;            //错误类型为“选项非法”
             return;                                //返回，不执行定时操作
    }
#endif

    OS_CRITICAL_ENTER();         //进入临界段
    p_tmr->State          = (OS_STATE           )OS_TMR_STATE_STOPPED;  //初始化定时器指标
    p_tmr->Type           = (OS_OBJ_TYPE        )OS_OBJ_TYPE_TMR;
    p_tmr->NamePtr        = (CPU_CHAR          *)p_name;
    p_tmr->Dly            = (OS_TICK            )dly;
    p_tmr->Match          = (OS_TICK            )0;
    p_tmr->Remain         = (OS_TICK            )0;
    p_tmr->Period         = (OS_TICK            )period;
    p_tmr->Opt            = (OS_OPT             )opt;
    p_tmr->CallbackPtr    = (OS_TMR_CALLBACK_PTR)p_callback;
    p_tmr->CallbackPtrArg = (void              *)p_callback_arg;
    p_tmr->NextPtr        = (OS_TMR            *)0;
    p_tmr->PrevPtr        = (OS_TMR            *)0;

#if OS_CFG_DBG_EN > 0u           //如果使能（默认使能）了调试代码和变量 
    OS_TmrDbgListAdd(p_tmr);     //将该定时添加到定时器双向调试链表
#endif
    OSTmrQty++;                  //定时器个数加1

    OS_CRITICAL_EXIT_NO_SCHED(); //退出临界段（无调度）
   *p_err = OS_ERR_NONE;         //错误类型为“无错误”
}
```

定时器创建函数比较简单，主要是根据用户指定的参数将定时器控制块进行相关初始化，并且定时器状态会被设置为 OS_TMR_STATE_STOPPED。



软件定时器创建函数OSTmrCreate()使用实例：

```c
OS_ERR      err; 
OS_TMR      my_tmr;   //声明软件定时器对象 

/* 创建软件定时器 */ 
OSTmrCreate ((OS_TMR              *)&my_tmr,             //软件定时器对象 
             (CPU_CHAR            *)"MySoftTimer",       //命名软件定时器 
             (OS_TICK              )10,                   
             //定时器初始值，依10Hz 时基计算，即为1s 
             (OS_TICK              )10,                   
             //定时器周期重载值，依10Hz 时基计算，即为1s 
             (OS_OPT               )OS_OPT_TMR_PERIODIC, //周期性定时 
             (OS_TMR_CALLBACK_PTR  )TmrCallback,         //回调函数 
             (void                *)"Timer Over!",      //传递实参给回调函数 
             (OS_ERR              *)err);                //返回错误类型 
```



### 启动软件定时器函数OSTmrStart()

在**系统初始化的时候会自动创建一个软件定时器任务**，在这个任务中，如果暂时没有运行中的定时器，任务会进入阻塞态等待定时器任务节拍的信号量。我们在创建一个软件定时器之后，如果没有启动它，该定时器就不会被添加到软件定时器列表中，那么在定时器任务就不会运行该定时器，而 OSTmrStart() 函数就是**将已经创建的软件定时器添加到定时器列表中**，这样子被创建的定时器就会被系统运行。

OSTmrStart() 源码：

```c
CPU_BOOLEAN  OSTmrStart (OS_TMR  *p_tmr,  //定时器控制块指针
                         OS_ERR  *p_err)  //返回错误类型
{
    OS_ERR       err;
    CPU_BOOLEAN  success; //暂存函数执行结果

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return (DEF_FALSE);             //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能（默认使能）了中断中非法调用检测 
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数是在中断中被调用               
       *p_err = OS_ERR_TMR_ISR;                //错误类型为“在中断函数中定时”
        return (DEF_FALSE);                    //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u           //如果使能（默认使能）了参数检测
    if (p_tmr == (OS_TMR *)0) {      //如果使能 p_tmr 的实参为空
       *p_err = OS_ERR_TMR_INVALID;  //错误类型为“无效的定时器”
        return (DEF_FALSE);          //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u           //如果使能（默认使能）了对象类型检测
    if (p_tmr->Type != OS_OBJ_TYPE_TMR) { //如果该定时器的对象类型有误
       *p_err = OS_ERR_OBJ_TYPE;          //错误类型为“对象类型错误”
        return (DEF_FALSE);               //返回 DEF_FALSE，不继续执行
    }
#endif

    OSSchedLock(&err);                            //锁住调度器 ★
    switch (p_tmr->State) {                       //根据定时器的状态分类处理
        case OS_TMR_STATE_RUNNING:                //如果定时器正在运行，则重启
             OS_TmrUnlink(p_tmr);                 //从定时器轮里移除该定时器 ★
             OS_TmrLink(p_tmr, OS_OPT_LINK_DLY);  //将该定时器重新插入到定时器轮 ★
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_NONE;               //错误类型为“无错误”
             success = DEF_TRUE;                  //执行结果暂为 DEF_TRUE
             break;

        case OS_TMR_STATE_STOPPED:                //如果定时器已被停止，则开启  
        case OS_TMR_STATE_COMPLETED:              //如果定时器已完成了，则开启  
             OS_TmrLink(p_tmr, OS_OPT_LINK_DLY);  //将该定时器重新插入到定时器轮
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_NONE;               //错误类型为“无错误”
             success = DEF_TRUE;                  //执行结果暂为 DEF_TRUE
             break;

        case OS_TMR_STATE_UNUSED:                 //如果定时器未被创建
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_TMR_INACTIVE;       //错误类型为“定时器未激活”
             success = DEF_FALSE;                 //执行结果暂为 DEF_FALSE
             break;

        default:                                  //如果定时器的状态超出预期
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err = OS_ERR_TMR_INVALID_STATE;    //错误类型为“定时器无效”
             success = DEF_FALSE;                 //执行结果暂为 DEF_FALSE
             break;
    }
    return (success);                             //返回执行结果
}
```

- 「OSSchedLock(&err);」锁住调度器，因为接下来的操作是需要操作定时器列表的，此时应该锁定调度器，不被其他任务打扰，然后根据定时器的状态分类处理。
- 「OS_TmrLink(p_tmr, OS_OPT_LINK_DLY);」从定时器列表移除定时器之后需要将软件定时器重新按照周期插入定时器列表中，调用 OS_TmrLink() 函数即可将软件定时器插入定时器列表。
- 「OS_TmrUnlink(p_tmr);」如果定时器正在运行，则重启，首先调用 OS_TmrUnlink() 函数将运行中的定时器从原本的定时器列表中移除



OS_TmrLink() 源码：

```c
void  OS_TmrLink (OS_TMR  *p_tmr,  //定时器控制块指针
                  OS_OPT   opt)    //选项
{
    OS_TMR_SPOKE     *p_spoke;
    OS_TMR           *p_tmr0;
    OS_TMR           *p_tmr1;
    OS_TMR_SPOKE_IX   spoke;

    p_tmr->State = OS_TMR_STATE_RUNNING;                           //重置定时器为运行状态
    if (opt == OS_OPT_LINK_PERIODIC) {                             //如果定时器是再次插入
        p_tmr->Match = p_tmr->Period + OSTmrTickCtr;               //匹配时间加个周期重载值 ★
    } else {                                                       //如果定时器是首次插入
        if (p_tmr->Dly == (OS_TICK)0) {                            //如果定时器的 Dly = 0
            p_tmr->Match = p_tmr->Period + OSTmrTickCtr;           //匹配时间加个周期重载值 ★
        } else {                                                   //如果定时器的 Dly != 0
            p_tmr->Match = p_tmr->Dly    + OSTmrTickCtr;           //匹配时间加个 Dly ★
        }
    }
    spoke  = (OS_TMR_SPOKE_IX)(p_tmr->Match % OSCfg_TmrWheelSize); //通过哈希算法觉得将该定时器 ★
    p_spoke = &OSCfg_TmrWheel[spoke];                              //插入到定时器轮的哪个列表。

    if (p_spoke->FirstPtr ==  (OS_TMR *)0) {                //如果列表为空，
        p_tmr->NextPtr      = (OS_TMR *)0;                  //直接将该定时器作为列表的第一个元素。
        p_tmr->PrevPtr      = (OS_TMR *)0;
        p_spoke->FirstPtr   = p_tmr;
        p_spoke->NbrEntries = 1u;
    } else {                                                //如果列表非空
        p_tmr->Remain  = p_tmr->Match                       //算出定时器 p_tmr 的剩余时间
                       - OSTmrTickCtr;
        p_tmr1         = p_spoke->FirstPtr;                 //取列表的首个元素到 p_tmr1
        while (p_tmr1 != (OS_TMR *)0) {                     //如果 p_tmr1 非空
            p_tmr1->Remain = p_tmr1->Match                  //算出 p_tmr1 的剩余时间
                           - OSTmrTickCtr;
            if (p_tmr->Remain > p_tmr1->Remain) {       //如果 p_tmr 的剩余时间大于 p_tmr1 的
                if (p_tmr1->NextPtr  != (OS_TMR *)0) {  //如果 p_tmr1 后面非空
                    p_tmr1            = p_tmr1->NextPtr;//取p_tmr1后一个定时器为新的p_tmr1进行下一次循环
                } else {                                //如果 p_tmr1 后面为空
                    p_tmr->NextPtr    = (OS_TMR *)0;    //将 p_tmr 插到 p_tmr1 的后面，结束循环
                    p_tmr->PrevPtr    =  p_tmr1;
                    p_tmr1->NextPtr   =  p_tmr;             
                    p_tmr1            = (OS_TMR *)0;        
                }
            } else {                                        //如果 p_tmr 的剩余时间不大于 p_tmr1 的，
                if (p_tmr1->PrevPtr == (OS_TMR *)0) {       //将 p_tmr 插入到 p_tmr1 的前一个，结束循环
                    p_tmr->PrevPtr    = (OS_TMR *)0;
                    p_tmr->NextPtr    = p_tmr1;
                    p_tmr1->PrevPtr   = p_tmr;
                    p_spoke->FirstPtr = p_tmr;
                } else {                                   
                    p_tmr0            = p_tmr1->PrevPtr;
                    p_tmr->PrevPtr    = p_tmr0;
                    p_tmr->NextPtr    = p_tmr1;
                    p_tmr0->NextPtr   = p_tmr;
                    p_tmr1->PrevPtr   = p_tmr;
                }
                p_tmr1 = (OS_TMR *)0;                      
            }
        }
        p_spoke->NbrEntries++;                              //列表元素成员数加1
    }
    if (p_spoke->NbrEntriesMax < p_spoke->NbrEntries) {     //更新列表成员数最大值历史记录
        p_spoke->NbrEntriesMax = p_spoke->NbrEntries;
    }
}
```

- 「p_tmr->Match = p_tmr->Period + OSTmrTickCtr;」重置定时器为运行状态，如果定时器是再次插入，肯定是周期性定时器，延时时间为 Period，定时器的匹配时间（唤醒时间）Match 等于周期重载值 Period 加上当前的定时器计时时间。 
- 「p_tmr->Match = p_tmr->Period + OSTmrTickCtr;」如果定时器是首次插入，如果定时器的延时时间 Dly 等于 0，定时器的匹配时间 Match 也等于周期重载值加上当前的定时器计时时间。
- 「p_tmr->Match = p_tmr->Dly    + OSTmrTickCtr;」而如果定时器的 Dly 不等于 0，定时器的匹配时间 Match 则等于Dly 的值加上当前的定时器计时时间。
- 「spoke  = (OS_TMR_SPOKE_IX)(p_tmr->Match % OSCfg_TmrWheelSize);」通过哈希算法决定将该定时器插入到定时器的哪个列表，这与时基列表很像。既然是哈希算法，开始插入的时候也要根据余数进行操作，根据软件定时器的匹配时间对 OSCfg_TmrWheelSize 的余数取出 OSCfg_TmrWheel[OS_CFG_TMR_WHEEL_SIZE] 中对应的定时器列表记录，然后将定时器插入对应的列表中。 



OS_TmrUnlink() 源码：

```c
void  OS_TmrUnlink (OS_TMR  *p_tmr)   //定时器控制块指针
{
    OS_TMR_SPOKE    *p_spoke;
    OS_TMR          *p_tmr1;
    OS_TMR          *p_tmr2;
    OS_TMR_SPOKE_IX  spoke;

    spoke   = (OS_TMR_SPOKE_IX)(p_tmr->Match % OSCfg_TmrWheelSize); //与插入时一样，通过哈希算法找出 ★
    p_spoke = &OSCfg_TmrWheel[spoke];                               //该定时器在定时器轮的哪个列表。

    if (p_spoke->FirstPtr == p_tmr) {                       //如果 p_tmr 是列表的首个元素
        p_tmr1            = (OS_TMR *)p_tmr->NextPtr;       //取 p_tmr 后一个元素为 p_tmr1(可能为空)
        p_spoke->FirstPtr = (OS_TMR *)p_tmr1;               //表首改为 p_tmr1 
        if (p_tmr1 != (OS_TMR *)0) {                        //如果 p_tmr1 确定非空
            p_tmr1->PrevPtr = (OS_TMR *)0;                  //p_tmr1 的前面清空
        }
    } else {                                                //如果 p_tmr 不是列表的首个元素
        p_tmr1          = (OS_TMR *)p_tmr->PrevPtr;         //将 p_tmr 从列表移除，并将 p_tmr 
        p_tmr2          = (OS_TMR *)p_tmr->NextPtr;         //前后的两个元素连接在一起.
        p_tmr1->NextPtr = p_tmr2;
        if (p_tmr2 != (OS_TMR *)0) {                        
            p_tmr2->PrevPtr = (OS_TMR *)p_tmr1;
        }
    }
    p_tmr->State   = OS_TMR_STATE_STOPPED;   //复位 p_tmr 的指标             
    p_tmr->NextPtr = (OS_TMR *)0;
    p_tmr->PrevPtr = (OS_TMR *)0;
    p_spoke->NbrEntries--;                   //列表元素成员减1
}
```



OSTmrStart() 使用实例：

```c
OS_ERR      err; 
OS_TMR      my_tmr;   //声明软件定时器对象 

/* 创建软件定时器 */ 
OSTmrCreate ((OS_TMR              *)&my_tmr,             //软件定时器对象 
             (CPU_CHAR            *)"MySoftTimer",       //命名软件定时器 
             (OS_TICK              )10,                   
             //定时器初始值，依10Hz 时基计算，即为1s 
             (OS_TICK              )10,                   
             //定时器周期重载值，依10Hz 时基计算，即为1s 
             (OS_OPT               )OS_OPT_TMR_PERIODIC, //周期性定时 
             (OS_TMR_CALLBACK_PTR  )TmrCallback,         //回调函数 
             (void                *)"Timer Over!",     //传递实参给回调函数 
             (OS_ERR              *)err);                //返回错误类型 

/* 启动软件定时器 */ 
OSTmrStart ((OS_TMR   *)&my_tmr, //软件定时器对象 
            (OS_ERR   *)err);    //返回错误类型
```



### 软件定时器列表管理

有些情况下，当系统中有多个软件定时器的时候，uCOS 可能要维护上百个定时器。使用定时器列表会大大降低更新定时器列表所占用的 CPU 时间，一个一个检测是否到期效率很低，有没有什么办法让系统快速查找到到期的软件定时器？uCOS 对软件定时器列表的管理就跟时间节拍一样，采用哈希算法。OS_TmrLink 将不同的定时器变量根据其对 OSCfg_TmrWheelSize 余数的不同插入到数 组OSCfg_TmrWheel[OS_CFG_TMR_WHEEL_SIZE]中去，uCOS 的软件定时器列表示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626110813.png" width="450px" /> </div>

定时器列表中包含 OS_CFG_TMR_WHEEL_SIZE 条记录，该值是一个宏定义，由用户指定，在 os_cfg_app.h 文件中。能记录定时器的多少仅限于处理器的 RAM 空间，推荐的设置值为定时器数/4。定时器列表的每个记录都由 3 部分组成：

- NbrEntriesMax 表明该记录中有多少个定时器；
- NbrEntriesMax 表明该记录中最大时存放了多少个定时器；
- FirstPtr 指向当前记录的定时器链表。

 

下面举个例子来讲述软件定时器采用哈希算法插入到对应的定时器列表中的过程：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626111017.png" width="700px" /> </div>

先假定此时的定时器列表是空的，设置的宏定义 OS_CFG_TMR_WHEEL_SIZE 为 9，当前的 OSTmrTickCtr 为 12。我们调用 OSTmrStart() 函数将定时器插入定时器列表。假定定时器创建时 dly 的值为 1，并且这个任务是单次定时模式。因为STmrTickCtr 的值为 12，定时器的定时值为 1，那么在插入定时器列表的时候，定时器的唤醒时间 Match 为 13（Match = Dly + OSTmrTickCtr），经过哈希算法，得到 spoke = 4，该定时器会被放入定时器会被插入 OSCfg_TmrWheel[4] 列表中，因为当前定时器列表是空的，OS_TMR 会被放在队列中的首位置 (OSCfg_TmrWheel[4] 中成员变量FirstPtr 将 指向这个 OS_TMR)，并且索引 4 的计数值加一（OSCfg_TmrWheel[4]的成员变量 NbrEntries 为 1）。定时器的匹配值 Match 被放在 OS_TMR 的 Match 成员变量中。因为新插入的定时器是索引 4 的唯一一个定时器，所有定时器的 NextPtr 和 PrevPtr 都指向NULL（也就是 0）

如果系统此时再插入一个周期 Period 为 10 的定时器定时器，定时器的唤醒时间 Match为 22（Match = Period + OSTmrTickCtr），那么经过哈希算法，得到 spoke = 4，该定时器会被放入定时器会被插入 OSCfg_TmrWheel[4]列表中，但是由于 OSCfg_TmrWheel[4]列表已有一个软件定时器，那么第二个软件定时器会根据 Remain 的值按照升序进行插入操作，插入完成示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626115612.png" width="800px" /> </div>



### 停止定时器函数OSTmrStop()

OSTmrStop() 函数用于停止一个软件定时器。软件定时器被停掉之后可以调用 OSTmrStart() 函数重启，但是**重启之后定时器是从头计时，而不是接着上次停止的时刻继续计时**。

OSTmrStop() 函数源码：

```c
CPU_BOOLEAN  OSTmrStop (OS_TMR  *p_tmr,          //定时器控制块指针
                        OS_OPT   opt,            //选项
                        void    *p_callback_arg, //传给回调函数的新参数
                        OS_ERR  *p_err)          //返回错误类型
{
    OS_TMR_CALLBACK_PTR  p_fnct;
    OS_ERR               err;
    CPU_BOOLEAN          success;  //暂存函数执行结果



#ifdef OS_SAFETY_CRITICAL                //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
        return (DEF_FALSE);              //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能（默认使能）了中断中非法调用检测 
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数是在中断中被调用 
       *p_err = OS_ERR_TMR_ISR;                //错误类型为“在中断函数中定时”
        return (DEF_FALSE);                    //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u          //如果使能（默认使能）了参数检测
    if (p_tmr == (OS_TMR *)0) {     //如果使能 p_tmr 的实参为空
       *p_err = OS_ERR_TMR_INVALID; //错误类型为“无效的定时器”
        return (DEF_FALSE);         //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u            //如果使能（默认使能）了对象类型检测
    if (p_tmr->Type != OS_OBJ_TYPE_TMR) {  //如果该定时器的对象类型有误
       *p_err = OS_ERR_OBJ_TYPE;           //错误类型为“对象类型错误”
        return (DEF_FALSE);                //返回 DEF_FALSE，不继续执行
    }
#endif

    OSSchedLock(&err);                                                   //锁住调度器  
    switch (p_tmr->State) {                                              //根据定时器的状态分类处理
        case OS_TMR_STATE_RUNNING:                                       //如果定时器正在运行
             OS_TmrUnlink(p_tmr);                            //★        //从定时器轮列表里移除该定时器
            *p_err = OS_ERR_NONE;                                        //错误类型为“无错误”
             switch (opt) {                                              //根据选项分类处理
                 case OS_OPT_TMR_CALLBACK:                   //★        //执行回调函数，使用创建定时器时的实参
                      p_fnct = p_tmr->CallbackPtr;                       //取定时器的回调函数 
                      if (p_fnct != (OS_TMR_CALLBACK_PTR)0) {            //如果回调函数存在 
                        (*p_fnct)((void *)p_tmr, p_tmr->CallbackPtrArg); //使用创建定时器时的实参执行回调函数
                      } else {                                           //如果回调函数不存在 
                         *p_err = OS_ERR_TMR_NO_CALLBACK;                //错误类型为“定时器没有回调函数”
                      }
                      break;

                 case OS_OPT_TMR_CALLBACK_ARG:                    //执行回调函数，使用 p_callback_arg 作为实参
                      p_fnct = p_tmr->CallbackPtr;                //取定时器的回调函数 
                      if (p_fnct != (OS_TMR_CALLBACK_PTR)0) {     //如果回调函数存在 
                        (*p_fnct)((void *)p_tmr, p_callback_arg); //使用 p_callback_arg 作为实参执行回调函数
                      } else {                                    //如果回调函数不存在 
                         *p_err = OS_ERR_TMR_NO_CALLBACK;         //错误类型为“定时器没有回调函数”
                      }
                      break;

                 case OS_OPT_TMR_NONE:           //只需停掉定时器
                      break;

                 default:                        //情况超出预期
                     OSSchedUnlock(&err);        //解锁调度器
                    *p_err = OS_ERR_OPT_INVALID; //错误类型为“选项无效”
                     return (DEF_FALSE);         //返回 DEF_FALSE，不继续执行
             }
             OSSchedUnlock(&err);
             success = DEF_TRUE;
             break;

        case OS_TMR_STATE_COMPLETED:            //如果定时器已完成第一次定时                     
        case OS_TMR_STATE_STOPPED:              //如果定时器已被停止                 
             OSSchedUnlock(&err);               //解锁调度器
            *p_err   = OS_ERR_TMR_STOPPED;      //错误类型为“定时器已被停止”
             success = DEF_TRUE;                //执行结果暂为 DEF_TRUE
             break;

        case OS_TMR_STATE_UNUSED:               //如果该定时器未被创建过                    
             OSSchedUnlock(&err);               //解锁调度器
            *p_err   = OS_ERR_TMR_INACTIVE;     //错误类型为“定时器未激活”
             success = DEF_FALSE;               //执行结果暂为 DEF_FALSE
             break;

        default:                                //如果定时器状态超出预期
             OSSchedUnlock(&err);               //解锁调度器
            *p_err   = OS_ERR_TMR_INVALID_STATE;//错误类型为“定时器状态非法”
             success = DEF_FALSE;               //执行结果暂为 DEF_FALSE
             break;
    }
    return (success);                           //返回执行结果
}
```

- 「case OS_OPT_TMR_CALLBACK:」如果需要执行回调函数，并且使用创建定时器时的实参，那就取定时器的回调函数，如果回调函数存在，就根据创建定时器指定的实参执行回调函数。



OSTmrStop()使用实例：

```c
OS_ERR      err; 
OS_TMR      my_tmr;   //声明软件定时器对象 
OSTmrStop ((OS_TMR   *)&my_tmr,           //定时器控制块指针 
           (OS_OPT     )OS_OPT_TMR_NONE,  //选项 
           (void      *)"Timer Over!",    //传给回调函数的新参数 
           (OS_ERR    *)err);             //返回错误类型 
```



### 删除软件定时器函数OSTmrDel()

OSTmrDel() 用于删除一个已经被创建成功的软件定时器，删除之后就无法使用该定时器，并且定时器相应的信息也会被系清空。

OSTmrDel() 源码：

```c
#if OS_CFG_TMR_DEL_EN > 0u             //如果使能（默认是嫩）了 OSTmrDel() 函数
CPU_BOOLEAN  OSTmrDel (OS_TMR  *p_tmr, //定时器控制块指针
                       OS_ERR  *p_err) //返回错误类型
{
    OS_ERR       err;
    CPU_BOOLEAN  success;  //暂存函数执行结果



#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return (DEF_FALSE);             //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能（默认使能）了中断中非法调用检测 
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数是在中断中被调用 
       *p_err  = OS_ERR_TMR_ISR;                //错误类型为“在中断函数中定时”
        return (DEF_FALSE);                     //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u          //如果使能（默认使能）了参数检测
    if (p_tmr == (OS_TMR *)0) {     //如果使能 p_tmr 的实参为空
       *p_err = OS_ERR_TMR_INVALID; //错误类型为“无效的定时器”
        return (DEF_FALSE);         //返回 DEF_FALSE，不继续执行
    }
#endif

#if OS_CFG_OBJ_TYPE_CHK_EN > 0u            //如果使能（默认使能）了对象类型检测
    if (p_tmr->Type != OS_OBJ_TYPE_TMR) {  //如果该定时器的对象类型有误
       *p_err = OS_ERR_OBJ_TYPE;           //错误类型为“对象类型错误”
        return (DEF_FALSE);                //返回 DEF_FALSE，不继续执行
    }
#endif

    OSSchedLock(&err);          //锁住调度器   
#if OS_CFG_DBG_EN > 0u          //如果使能（默认使能）了调试代码和变量 
    OS_TmrDbgListRemove(p_tmr); //将该定时从定时器双向调试链表移除
#endif
    OSTmrQty--;                 //定时器个数减1

    switch (p_tmr->State) {                       //根据定时器的状态分类处理
        case OS_TMR_STATE_RUNNING:                //如果定时器正在运行
             OS_TmrUnlink(p_tmr);                 //从当前定时器轮列表移除定时器 ★
             OS_TmrClr(p_tmr);                    //复位定时器的指标
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_NONE;               //错误类型为“无错误”
             success = DEF_TRUE;                  //执行结果暂为 DEF_TRUE
             break;

        case OS_TMR_STATE_STOPPED:                //如果定时器已被停止  
        case OS_TMR_STATE_COMPLETED:              //如果定时器已完成第一次定时
             OS_TmrClr(p_tmr);                    //复位定时器的指标
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_NONE;               //错误类型为“无错误”
             success = DEF_TRUE;                  //执行结果暂为 DEF_TRUE
             break;
             
        case OS_TMR_STATE_UNUSED:                 //如果定时器已被删除
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_TMR_INACTIVE;       //错误类型为“定时器未激活”
             success = DEF_FALSE;                 //执行结果暂为 DEF_FALSE
             break;

        default:                                  //如果定时器的状态超出预期
             OSSchedUnlock(&err);                 //解锁调度器
            *p_err   = OS_ERR_TMR_INVALID_STATE;  //错误类型为“定时器无效”
             success = DEF_FALSE;                 //执行结果暂为 DEF_FALSE
             break;
    }
    return (success);                             //返回执行结果
}
#endif
```



## 6. 软件定时器任务

软件定时器的回调函数的上下文是在任务中，所以，系统中必须要一个任务来管理所有的软件定时器，等到定时时间到达后就调用定时器对应的回调函数。

创建软件定时器任务 OS_TmrInit()：

```c
void  OS_TmrInit (OS_ERR  *p_err)
{
    OS_TMR_SPOKE_IX   i;
    OS_TMR_SPOKE     *p_spoke;



#ifdef OS_SAFETY_CRITICAL
    if (p_err == (OS_ERR *)0) {
        OS_SAFETY_CRITICAL_EXCEPTION();
        return;
    }
#endif

#if OS_CFG_DBG_EN > 0u
    OSTmrDbgListPtr = (OS_TMR *)0;
#endif

    if (OSCfg_TmrTaskRate_Hz > (OS_RATE_HZ)0) { // ★
        OSTmrUpdateCnt = OSCfg_TickRate_Hz / OSCfg_TmrTaskRate_Hz;
    } else {
        OSTmrUpdateCnt = OSCfg_TickRate_Hz / (OS_RATE_HZ)10;
    }
    OSTmrUpdateCtr   = OSTmrUpdateCnt;

    OSTmrTickCtr     = (OS_TICK)0;

    OSTmrTaskTimeMax = (CPU_TS)0;

    for (i = 0u; i < OSCfg_TmrWheelSize; i++) {
        p_spoke                = &OSCfg_TmrWheel[i];
        p_spoke->NbrEntries    = (OS_OBJ_QTY)0;
        p_spoke->NbrEntriesMax = (OS_OBJ_QTY)0;
        p_spoke->FirstPtr      = (OS_TMR   *)0;
    }

    /* ---------------- CREATE THE TIMER TASK --------------- */
    if (OSCfg_TmrTaskStkBasePtr == (CPU_STK*)0) {
       *p_err = OS_ERR_TMR_STK_INVALID;
        return;
    }

    if (OSCfg_TmrTaskStkSize < OSCfg_StkSizeMin) {
       *p_err = OS_ERR_TMR_STK_SIZE_INVALID;
        return;
    }

    if (OSCfg_TmrTaskPrio >= (OS_CFG_PRIO_MAX - 1u)) {
       *p_err = OS_ERR_TMR_PRIO_INVALID;
        return;
    }
	
    // ★
    OSTaskCreate((OS_TCB     *)&OSTmrTaskTCB,
                 (CPU_CHAR   *)((void *)"uC/OS-III Timer Task"),
                 (OS_TASK_PTR )OS_TmrTask,
                 (void       *)0,
                 (OS_PRIO     )OSCfg_TmrTaskPrio,
                 (CPU_STK    *)OSCfg_TmrTaskStkBasePtr,
                 (CPU_STK_SIZE)OSCfg_TmrTaskStkLimit,
                 (CPU_STK_SIZE)OSCfg_TmrTaskStkSize,
                 (OS_MSG_QTY  )0,
                 (OS_TICK     )0,
                 (void       *)0,
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR | OS_OPT_TASK_NO_TLS),
                 (OS_ERR     *)p_err);
}
```

- 「if (OSCfg_TmrTaskRate_Hz > (OS_RATE_HZ)0) 」正常来说定时器任务的执行频率 OSCfg_TmrTaskRate_Hz 是大于 0 的，并且能被 OSCfg_TickRate_Hz 整除，才能比较准确得到定时器任务运行的频率。如果 OSCfg_TmrTaskRate_Hz 设置为大于 0，就配置定时器任务的频率。 

- 否则就配置为系统时钟频率的十分之一（1/10）。不过当设定的定时器的频率大于时钟节拍的执行频率的时候，定时器运行就会出错，但是这里没有进行判断，我们自己在写代码的时候注意一下即可。 

  举个例子，系统的 OSCfg_TickRate_Hz 是 1000，OSCfg_TmrTaskRate_Hz 是 10，那么计算得到 OSTmrUpdateCnt 就 是 100 ， 开始 的 时候 OSTmrUpdateCtr 是跟 OSTmrUpdateCnt 一样大的，都是 100，每当时钟节拍到来的时候 OSTmrUpdateCtr 就减 1，减到 0 的话就运行定时器任务，这样子就实现了从时间节拍中分频得到定时器任务频率。如果 OSCfg_TmrTaskRate_Hz 不能被 OSCfg_TickRate_Hz 整除，比如 OSCfg_TickRate_Hz 设置为 1000，OSCfg_TmrTaskRate_Hz 设置为 300，这样子设置是想要定时器任务执行频率是 300Hz，但是 OSTmrUpdateCnt 计算出来是 3，这样子定时器任务的执行频率大约就是 330Hz，定时的单位本来想设置为 3.3ms，可实际运行的单位却是 3ms，这样子肯定导致定时器不是很精确的，这些处理还是需要我们根据实际情况进行调整的。 



OS_TmrTask() 源码：

```c
void  OS_TmrTask (void  *p_arg) 
{ 
    CPU_BOOLEAN          done; 
    OS_ERR               err; 
    OS_TMR_CALLBACK_PTR  p_fnct; 
    OS_TMR_SPOKE        *p_spoke; 
    OS_TMR              *p_tmr; 
    OS_TMR              *p_tmr_next; 
    OS_TMR_SPOKE_IX      spoke; 
    CPU_TS               ts; 
    CPU_TS               ts_start; 
    CPU_TS               ts_end; 

    p_arg = p_arg;    /* Not using 'p_arg', prevent compiler warning */ 

    while (DEF_ON) 
    { 
        /* ★ 等待信号指示更新定时器的时间*/ 
        (void)OSTaskSemPend((OS_TICK )0, 
                            (OS_OPT  )OS_OPT_PEND_BLOCKING, 
                            (CPU_TS *)&ts, 
                            (OS_ERR *)&err);

        OSSchedLock(&err); 
        ts_start = OS_TS_GET(); 
        /* 增加当前定时器时间*/ 
        OSTmrTickCtr++;

        /* 通过哈希算法找到对应时间唤醒的列表 */
        spoke    = (OS_TMR_SPOKE_IX)(OSTmrTickCtr % OSCfg_TmrWheelSize); 
        p_spoke = &OSCfg_TmrWheel[spoke];

        /* 获取列表头部的定时器 */ 
        p_tmr = p_spoke->FirstPtr;

        done     = DEF_FALSE; 
        while (done == DEF_FALSE) 
        { 

            if (p_tmr != (OS_TMR *)0)
            { 
                /*  指向下一个定时器以进行更新， 
                 因为可能当前定时器到时了会从列表中移除 */ 
                p_tmr_next = (OS_TMR *)p_tmr->NextPtr;  

                /* 确认是定时时间到达 */ 
                if (OSTmrTickCtr == p_tmr->Match)
                { 
                    /* 先移除定时器 */ 
                    OS_TmrUnlink(p_tmr);  

                    /* 如果是周期定时器 */ 
                    if (p_tmr->Opt == OS_OPT_TMR_PERIODIC) 
                    { 
                        /*  重新按照唤醒时间插入定时器列表 */ 
                        OS_TmrLink(p_tmr, 
                                   OS_OPT_LINK_PERIODIC);
                    } 
                    else 
                    { 
                        /* 定时器状态设置为已完成 */ 
                        p_tmr->State = OS_TMR_STATE_COMPLETED;
                    } 
                    /* 执行回调函数（如果可用）*/ 
                    p_fnct = p_tmr->CallbackPtr; 
                    if (p_fnct != (OS_TMR_CALLBACK_PTR)0) 
                    { 
                        (*p_fnct)((void *)p_tmr, 
                                  p_tmr->CallbackPtrArg);
                    } 
                    /* 看看下一个计时器是否匹配 */ 
                    p_tmr = p_tmr_next;
                } 
                else 
                { 
                    done  = DEF_TRUE; 
                } 
            } 
            else 
            { 
                done = DEF_TRUE; 
            } 
        } 
        /* ★ 测量定时器任务的执行时间*/ 
        ts_end = OS_TS_GET() - ts_start; 
        OSSchedUnlock(&err); 
        if (OSTmrTaskTimeMax < ts_end) 
        { 
            OSTmrTaskTimeMax = ts_end; 
        } 
    } 
} 
```

- 「(void)OSTaskSemPend((OS_TICK )0...」调用 OSTaskSemPend() 函数在一直等待定时器节拍的信号量，等待到了才运行。定时器节拍的运行：**系统的时钟节拍是基于 SysTick 定时器上的，uCOS 采用 Tick 任务（OS_TickTask）管理系统的时间节拍，而定时器节拍是由系统节拍分频而来，那么其发送信号量的地方当然也是在 SysTick 中断服务函数中**。但是 uCOS 支持采用中断延迟，如果使用了**中断延迟**，那么发送任务信号量的地方就会在中断发布任务中（OS_IntQTask），从代码中，我们可以看到当 OSTmrUpdateCtr 减到 0 的时候才会发送一次信号量，这也就是为什么我们的定时器节拍是基于系统时钟节拍分频而来的原因。

  注意：此处的信号量获取是任务信号量而非内核对象的信号量

- 「ts_end = OS_TS_GET() - ts_start;...」当定时器任务被执行，它**首先递增 OSTmrTickCtr 变量**，然后通过**哈希算法决定哪个定时器列表需被更新**。然后，如果这个定时器列表中存在定时器（FirstPtr 不为 NULL），系统会**检查定时器中的匹配时间 Match 是否与当前定时器时间 OSTmrTickCtr 相等，如果相等，这个定时器会被移出该定时器，然后调用这个定时器的回调函数**（假定这个定时器被创建时有回调函数），再**根据定时器的工作模式决定是否重新插入定时器列表中**。然后**遍历该定时器列表直到没有定时器的 Match 值与 OSTmrTickCtr 匹配**。

  注意：当定时器被唤醒后，定时器列表会被重新排序，定时器也不一定插入原本的定时器列表中。

- OS_TmrTask() 任务的大部分工作都是在锁调度器的状态下进行的。然而，因为定时器列表会被重新分配（依次排序），所以遍历这个定时器列表的时间会非常短的，也就是临界段会非常短的。 



定时器任务的发送信号量位置

```c
/***************************在SysTick 中断服务函数中************************/ 

#if OS_CFG_TMR_EN > 0u                                
//如果使能（默认使能）了软件定时器 
OSTmrUpdateCtr--;                                //软件定时器计数器自减 
if (OSTmrUpdateCtr == (OS_CTR)0u)                //如果软件定时器计数器减至0 
{ 
    OSTmrUpdateCtr = OSTmrUpdateCnt;             //重载软件定时器计数器 
    //★ 发送信号量给软件定时器任务OS_TmrTask() 
    OSTaskSemPost((OS_TCB *)&OSTmrTaskTCB,                 
                  (OS_OPT  ) OS_OPT_POST_NONE, 
                  (OS_ERR *)&err); 
} 
#endif 

/*********************在中断发布任务中**********************************/ 

#if OS_CFG_TMR_EN > 0u 
OSTmrUpdateCtr--; 
if (OSTmrUpdateCtr == (OS_CTR)0u) 
{ 
    OSTmrUpdateCtr = OSTmrUpdateCnt; 
    ts             = OS_TS_GET();         /* 获取时间戳 */ 
    //★ 发送信号量给软件定时器任务 OS_TmrTask()
    (void)OS_TaskSemPost((OS_TCB *)&OSTmrTaskTCB, 
                         (OS_OPT  ) OS_OPT_POST_NONE, 
                         (CPU_TS  ) ts, 
                         (OS_ERR *)&err); 
} 
#endif
```



# 任务信号量

## 1. 任务信号量的基本概念

uCOS 提供任务信号量这个功能，**每个任务都有一个 32 位**（用户可以自定义位宽，我们使用 32 位的 CPU，此处就是 32 位）的**信号量值 SemCtr**，这个信号量值是**「在任务控制块中包含的」**，是任务独有的一个信号量通知值，在大多数情况下，任务信号量可以替代内核对象的二值信号量、计数信号量等。 

相对于前面使用 uCOS 内核通信的资源，必须创建二进制信号量、计数信号量等情况，使用任务信号量显然更灵活。

**任务信号量的优点**：

- 使用任务信号量比通过内核对象信号量通信方式解除阻塞的任务的**「速度快」**
- 并且更加**「节省 RAM」** 内存空间
- 任务信号量的使用**「无需单独创建信号量」**

通过对任务信号量的合理使用，可以在一定场合下替代 uCOS 的信号量，用户只需向任务内部的信号量发送一个信号而不用通过外部的信号量进行发送，这样子处理就会很方便并且更加高效。

**任务信号量的缺点**：

**「只能有一个任务接收任务信号量」**，因为必须指定接收信号量的任务，才能正确发送信号量；而内核对象的信号量则没有这个限制，用户在释放信号量，可以采用广播的方式，让所有等待信号量的任务都获取到信号量。



在实际任务间的通信中，一个或多个任务发送一个信号量给另一个任务是非常常见的， 而一个任务给多个任务发送信号量的情况相对比较少。**「一个或多个任务发送一个信号量给另一个任务的情况就很适合采用任务信号量进行传递信号」**，如果任务信号量可以满足设计需求，那么尽量不要使用普通信号量，这样设计的系统会更加高效。



## 2. 任务信号量的函数接口

### 任务信号量释放函数OSTaskSemPost()

函数 OSTaskSemPost()用来释放任务信号量，虽然只有拥有任务信号量的任务才可以等待该任务信号量，但是其他所有的任务或者中断都可以向该任务释放信号量。

OSTaskSemPost() 源码：

```c
OS_SEM_CTR  OSTaskSemPost (OS_TCB  *p_tcb,   //目标任务
                           OS_OPT   opt,     //选项
                           OS_ERR  *p_err)   //返回错误类型
{
    OS_SEM_CTR  ctr;
    CPU_TS      ts;



#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果 p_err 为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((OS_SEM_CTR)0);         //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                  //如果使能（默认使能）了参数检测功能
    switch (opt) {                          //根据选项分类处理
        case OS_OPT_POST_NONE:              //如果选项在预期之内
        case OS_OPT_POST_NO_SCHED:
             break;                         //跳出

        default:                            //如果选项超出预期
            *p_err =  OS_ERR_OPT_INVALID;   //错误类型为“选项非法”
             return ((OS_SEM_CTR)0u);       //返回0（有错误），停止执行
    }
#endif

    ts = OS_TS_GET();                                      //获取时间戳

#if OS_CFG_ISR_POST_DEFERRED_EN > 0u                       //如果使能了中断延迟发布
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {             //如果该函数是在中断中被调用
        OS_IntQPost((OS_OBJ_TYPE)OS_OBJ_TYPE_TASK_SIGNAL,  //将该信号量发布到中断消息队列
                    (void      *)p_tcb,
                    (void      *)0,
                    (OS_MSG_SIZE)0,
                    (OS_FLAGS   )0,
                    (OS_OPT     )0,
                    (CPU_TS     )ts,
                    (OS_ERR    *)p_err);
        return ((OS_SEM_CTR)0);                           //返回0（尚未发布）   
    }
#endif

    ctr = OS_TaskSemPost(p_tcb,                          //将信号量按照普通方式处理
                         opt,
                         ts,
                         p_err);

    return (ctr);                                       //返回信号的当前计数值
}
```

- 如果使能了中断延迟发布，并且该函数在中断中被调用，那就将信号量发布到中断消息队列，由中断消息队列发布任务信号量。

- 调用 OS_TaskSemPost() 函数将信号量发布到任务中。

OS_TaskSemPost() 源码：

```c
OS_SEM_CTR  OS_TaskSemPost (OS_TCB  *p_tcb,   //目标任务
                            OS_OPT   opt,     //选项
                            CPU_TS   ts,      //时间戳
                            OS_ERR  *p_err)   //返回错误类型
{
    OS_SEM_CTR  ctr;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

    OS_CRITICAL_ENTER();                               //进入临界段
    if (p_tcb == (OS_TCB *)0) {                        //如果 p_tcb 为空
        p_tcb = OSTCBCurPtr;                           //将任务信号量发给自己（任务）
    }
    p_tcb->TS = ts;                                    //记录信号量被发布的时间戳
   *p_err     = OS_ERR_NONE;                           //错误类型为“无错误”
    switch (p_tcb->TaskState) {                        //跟吴目标任务的任务状态分类处理
        case OS_TASK_STATE_RDY:                        //如果目标任务没有等待状态
        case OS_TASK_STATE_DLY:
        case OS_TASK_STATE_SUSPENDED:
        case OS_TASK_STATE_DLY_SUSPENDED:
             switch (sizeof(OS_SEM_CTR)) {                        //判断是否将导致该信
                 case 1u:                                         //号量计数值溢出，如
                      if (p_tcb->SemCtr == DEF_INT_08U_MAX_VAL) { //果溢出，则开中断，
                          OS_CRITICAL_EXIT();                     //返回错误类型为“计
                         *p_err = OS_ERR_SEM_OVF;                 //数值溢出”，返回0
                          return ((OS_SEM_CTR)0);                 //（有错误），不继续
                      }                                           //执行。
                      break;                                      

                 case 2u:
                      if (p_tcb->SemCtr == DEF_INT_16U_MAX_VAL) {
                          OS_CRITICAL_EXIT();
                         *p_err = OS_ERR_SEM_OVF;
                          return ((OS_SEM_CTR)0);
                      }
                      break;

                 case 4u:
                      if (p_tcb->SemCtr == DEF_INT_32U_MAX_VAL) {
                          OS_CRITICAL_EXIT();
                         *p_err = OS_ERR_SEM_OVF;
                          return ((OS_SEM_CTR)0);
                      }
                      break;

                 default:
                      break;
             }
             p_tcb->SemCtr++;                              //信号量计数值不溢出则加1
             ctr = p_tcb->SemCtr;                          //获取信号量的当前计数值
             OS_CRITICAL_EXIT();                           //退出临界段
             break;                                        //跳出

        case OS_TASK_STATE_PEND:                           //如果任务有等待状态
        case OS_TASK_STATE_PEND_TIMEOUT:
        case OS_TASK_STATE_PEND_SUSPENDED:
        case OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED:
             if (p_tcb->PendOn == OS_TASK_PEND_ON_TASK_SEM) { //如果正等待任务信号量
                 OS_Post((OS_PEND_OBJ *)0,                    //发布信号量给目标任务
                         (OS_TCB      *)p_tcb,
                         (void        *)0,
                         (OS_MSG_SIZE  )0u,
                         (CPU_TS       )ts);
                 ctr = p_tcb->SemCtr;                         //获取信号量的当前计数值
                 OS_CRITICAL_EXIT_NO_SCHED();                 //退出临界段（无调度）
                 if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0) { //如果选择了调度任务
                     OSSched();                               //调度任务
                 }
             } else {                                         //如果没等待任务信号量
                 switch (sizeof(OS_SEM_CTR)) {                         //判断是否将导致
                     case 1u:                                          //该信号量计数值
                          if (p_tcb->SemCtr == DEF_INT_08U_MAX_VAL) {  //溢出，如果溢出，
                              OS_CRITICAL_EXIT();                      //则开中断，返回
                             *p_err = OS_ERR_SEM_OVF;                  //错误类型为“计
                              return ((OS_SEM_CTR)0);                  //数值溢出”，返
                          }                                            //回0（有错误），
                          break;                                       //不继续执行。

                     case 2u:
                          if (p_tcb->SemCtr == DEF_INT_16U_MAX_VAL) {
                              OS_CRITICAL_EXIT();
                             *p_err = OS_ERR_SEM_OVF;
                              return ((OS_SEM_CTR)0);
                          }
                          break;

                     case 4u:
                          if (p_tcb->SemCtr == DEF_INT_32U_MAX_VAL) {
                              OS_CRITICAL_EXIT();
                             *p_err = OS_ERR_SEM_OVF;
                              return ((OS_SEM_CTR)0);
                          }
                          break;

                     default:
                          break;
                 }
                 p_tcb->SemCtr++;                            //信号量计数值不溢出则加1
                 ctr = p_tcb->SemCtr;                        //获取信号量的当前计数值
                 OS_CRITICAL_EXIT();                         //退出临界段
             }
             break;                                          //跳出

        default:                                             //如果任务状态超出预期
             OS_CRITICAL_EXIT();                             //退出临界段
            *p_err = OS_ERR_STATE_INVALID;                   //错误类型为“状态非法”
             ctr   = (OS_SEM_CTR)0;                          //清零 ctr
             break;                                          //跳出
    }
    return (ctr);                                            //返回信号量的当前计数值
}
```

- 如果目标任务为空，则表示将任务信号量释放给自己，那么 p_tcb 就指向当前任务。



在释放任务信号量的时候，系统**首先判断目标任务的状态**，**只有处于等待状态并且等待的是任务信号量那就调用 OS_Post() 函数让等待的任务就绪**（如果内核对象信号量的话，还会让任务脱离等待列表），所以任务信号量的操作是非常高效的；如果没有处于等待状态或者等待的不是任务信号量，那就直接将任务控制块的元素 SemCtr 加 1。最后返回任务信号量计数值。 

其实，不管是否使能了中断延迟发布，**最终都是调用 OS_TaskSemPost() 函数进行释放任务信号量**。只是使能了中断延迟发布的释放过程会比较曲折，中间会有许多插曲，这是中断管理范畴的内容，留到后面再作介绍。在 OS_TaskSemPost() 函数中，又会调用 OS_Post() 函数释放内核对象。OS_Post() 函数是一个底层的释放（发布）函数，它不仅仅用来释放（发布）任务信号量，还可以释放信号量、互斥信号量、消息队列、事件标志组或任务消息队列。注意：在这里，OS_Post()函数将任务信号量直接释放给目标任务。



OSTaskSemPost() 使用实例：

```c
OSTaskSemPost((OS_TCB  *)&AppTaskPendTCB,          //目标任务 
              (OS_OPT   )OS_OPT_POST_NONE,        //没选项要求 
              (OS_ERR  *)&err);                   //返回错误类型
```



### 获取任务信号量函数OSTaskSemPend()

与 OSTaskSemPost() 任务信号量释放函数相对应，OSTaskSemPend() 函数用于获取一个任务信号量，参数中没有指定某个任务去获取信号量，**实际上就是当前运行任务获取它自己拥有的任务信号量**，代码中通过 OSTCBCurPtr 获取当前正在运行的任务。

OSTaskSemPend() 源码：

```c
OS_SEM_CTR  OSTaskSemPend (OS_TICK   timeout,  //等待超时时间
                           OS_OPT    opt,      //选项
                           CPU_TS   *p_ts,     //返回时间戳
                           OS_ERR   *p_err)    //返回错误类型
{
    OS_SEM_CTR    ctr;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL                //如果使能了安全检测
    if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
        return ((OS_SEM_CTR)0);          //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;                //返回错误类型为“在中断中等待”
        return ((OS_SEM_CTR)0);                 //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                  //如果使能了参数检测
    switch (opt) {                          //根据选项分类处理
        case OS_OPT_PEND_BLOCKING:          //如果选项在预期内
        case OS_OPT_PEND_NON_BLOCKING:
             break;                         //直接跳出

        default:                            //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;    //错误类型为“选项非法”
             return ((OS_SEM_CTR)0);        //返回0（有错误），停止执行
    }
#endif

    if (p_ts != (CPU_TS *)0) {      //如果 p_ts 非空
       *p_ts  = (CPU_TS  )0;        //清零（初始化）p_ts
    }

    CPU_CRITICAL_ENTER();                        //关中断  
    if (OSTCBCurPtr->SemCtr > (OS_SEM_CTR)0) {   //如果任务信号量当前可用
        OSTCBCurPtr->SemCtr--;                   //信号量计数器减1
        ctr    = OSTCBCurPtr->SemCtr;            //获取信号量的当前计数值
        if (p_ts != (CPU_TS *)0) {               //如果 p_ts 非空
           *p_ts  = OSTCBCurPtr->TS;             //返回信号量被发布的时间戳
        }
#if OS_CFG_TASK_PROFILE_EN > 0u                  //如果使能了任务控制块的简况变量
        OSTCBCurPtr->SemPendTime = OS_TS_GET() - OSTCBCurPtr->TS;     //更新任务等待
        if (OSTCBCurPtr->SemPendTimeMax < OSTCBCurPtr->SemPendTime) { //任务信号量的
            OSTCBCurPtr->SemPendTimeMax = OSTCBCurPtr->SemPendTime;   //最长时间记录。
        }
#endif
        CPU_CRITICAL_EXIT();                     //开中断            
       *p_err = OS_ERR_NONE;                     //错误类型为“无错误”
        return (ctr);                            //返回信号量的当前计数值
    }
    /* 如果任务信号量当前不可用 */
    if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) {  //如果选择了不阻塞任务
        CPU_CRITICAL_EXIT();                              //开中断
       *p_err = OS_ERR_PEND_WOULD_BLOCK;                  //错误类型为“缺乏阻塞”
        return ((OS_SEM_CTR)0);                           //返回0（有错误），停止执行
    } else {                                              //如果选择了阻塞任务
        if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) {  //如果调度器被锁
            CPU_CRITICAL_EXIT();                          //开中断
           *p_err = OS_ERR_SCHED_LOCKED;                  //错误类型为“调度器被锁”
            return ((OS_SEM_CTR)0);                       //返回0（有错误），停止执行
        }
    }
    /* 如果调度器未被锁 */
    OS_CRITICAL_ENTER_CPU_EXIT();                         //锁调度器，重开中断                      
    OS_Pend((OS_PEND_DATA *)0,                            //阻塞任务，等待信号量。
            (OS_PEND_OBJ  *)0,                            //不需插入等待列表。
            (OS_STATE      )OS_TASK_PEND_ON_TASK_SEM,
            (OS_TICK       )timeout);
    OS_CRITICAL_EXIT_NO_SCHED();                          //开调度器（无调度）

    OSSched();                                            //调度任务
    /* 任务获得信号量后得以继续运行 */
    CPU_CRITICAL_ENTER();                                 //关中断
    switch (OSTCBCurPtr->PendStatus) {                    //根据任务的等待状态分类处理
        case OS_STATUS_PEND_OK:                           //如果任务成功获得信号量
             if (p_ts != (CPU_TS *)0) {                   //返回信号量被发布的时间戳
                *p_ts                    =  OSTCBCurPtr->TS;
#if OS_CFG_TASK_PROFILE_EN > 0u                           //更新最长等待时间记录
                OSTCBCurPtr->SemPendTime = OS_TS_GET() - OSTCBCurPtr->TS;
                if (OSTCBCurPtr->SemPendTimeMax < OSTCBCurPtr->SemPendTime) {
                    OSTCBCurPtr->SemPendTimeMax = OSTCBCurPtr->SemPendTime;
                }
#endif
             }
            *p_err = OS_ERR_NONE;                         //错误类型为“无错误”
             break;                                       //跳出

        case OS_STATUS_PEND_ABORT:                        //如果等待被中止
             if (p_ts != (CPU_TS *)0) {                   //返回被终止时的时间戳
                *p_ts  =  OSTCBCurPtr->TS;
             }
            *p_err = OS_ERR_PEND_ABORT;                   //错误类型为“等待被中止”
             break;                                       //跳出

        case OS_STATUS_PEND_TIMEOUT:                      //如果等待超时
             if (p_ts != (CPU_TS *)0) {                   //返回时间戳为0
                *p_ts  = (CPU_TS  )0;
             }
            *p_err = OS_ERR_TIMEOUT;                      //错误类型为“等待超时”
             break;                                       //跳出

        default:                                          //如果等待状态超出预期
            *p_err = OS_ERR_STATUS_INVALID;               //错误类型为“状态非法”
             break;                                       //跳出
    }                                                     
    ctr = OSTCBCurPtr->SemCtr;                            //获取信号量的当前计数值
    CPU_CRITICAL_EXIT();                                  //开中断
    return (ctr);                                         //返回信号量的当前计数值
}
```

- 如果调度器未被锁，锁调度器，重开中断，调用 OS_Pend()函数将当前任务进入阻塞状态以等待任务信号量。

在调用该函数的时候，系统先判断任务信号量是否可用，即检查任务信号量的计数值是否大于 0，如果大于 0，即表示可用，这个时候获取信号量，即将计数值减 1 后直接返回。如果信号量不可用，且当调度器没有被锁住时，用户希望在任务信号量不可用的时候进行阻塞任务以等待任务信号量可用，那么系统就会调用 OS_Pend()函数将任务脱离就绪列表，如果用户有指定超时时间，系统还要将该任务插入节拍列表。注意：**此处系统并没有将任务插入等待列表**。然后切换任务，处于就绪列表中最高优先级的任务通过任务调度获得 CPU 使用权，等到出现任务信号量被释放、任务等待任务信号量被强制停止、等待超时等情况，任务会从阻塞中恢复，等待任务信号量的任务重新获得 CPU 使用权，返回相关错误代码和任务信号量计数值，用户可以根据返回的错误知道任务退出等待状态的情况。



OSTaskSemPend() 使用实例：

```c
OSTaskSemPend ((OS_TICK   )0,                     //无期限等待 
               (OS_OPT    )OS_OPT_PEND_BLOCKING,  //如果信号量不可用就等待 
               (CPU_TS   *)&ts,                   //获取信号量被发布的时间戳 
               (OS_ERR   *)&err);                 //返回错误类型
```



# 任务消息队列

## 1. 任务消息队列的基本概念

任务消息队列跟任务信号量一样，均**隶属于某一个特定任务，不需单独创建**，任务在则任务消息队列在，**只有该任务才可以获取（接收）这个任务消息队列的消息，其他任务只能给这个任务消息队列发送消息，却不能获取**。任务消息队列与前面讲解的（普通）消息队列极其相似，只是任务消息队列已隶属于一个特定任务，所以它**不具有等待列表**，在操作的过程中省去了等待任务插入和移除列表的动作，所以工作原理相对更简单一点，**效率也比较高一些**。

**任务消息队列的优点**：任务消息队列**「处理更快」**，**「RAM 开销更小」**

​	通过对任务消息队列的合理使用，可以在一定场合下替代 uCOS 的消息队列，用户只需向任务内部的消息队列发送一个消息而	不用通过外部的消息队列进行发送，这样子处理就会很方便并且更加高效。

**任务消息队列的缺点** ：只能指定消息发送的对象，**「有且只有一个任务接收消息」**

​	而内核对象的消息队列则没有这个限制，用户在发送消息的时候，可以采用广播消息的方式，让所有等待该消息的任务都获取	到消息。 

在实际任务间的通信中，一个或多个任务发送一个消息给另一个任务是非常常见的，而一个任务给多个任务发送消息的情况相对比较少。**一个或多个任务发送一个消息给另一个任务就很适合采用任务消息队列进行传递消息**，如果任务消息队列可以满足设计需求，那么尽量不要使用普通消息队列，这样子设计的系统会更加高效。 

内核对象消息队列是用结构体 OS_Q 来管理的，包含了管理消息的元素 MsgQ 和管理等待列表的元素 PendList 等。而任务消息队列的结构体成员变量就少了 PendList，因为等待任务消息队列只有拥有任务消息队列本身的任务才可以进行获取，故任务消息队列不需要等待列表的相关数据结构。



任务消息队列数据结构：

```c
struct  os_msg_q 
{ 
    OS_MSG *InPtr; // 任务消息队列中进消息指针
    OS_MSG *OutPtr; // 任务消息队列中出消息指针
    OS_MSG_QTY NbrEntriesSize; // 任务消息队列中最大可用的消息个数
    OS_MSG_QTY NbrEntries; // 记录任务消息队列中当前的消息个数
    OS_MSG_QTY NbrEntriesMax; // 记录任务消息队列最多的时候拥有的消息个数
};
```

- NbrEntries 记录任务消息队列中当前的消息个数，每当发送一个消息到任务消息队列的时候，若任务没有在等待该消息，那么新发送的消息被插入任务消息队列后此值加 1，NbrEntries 的大小不能超过 NbrEntriesSize



## 2. 任务消息队列的函数接口

### 任务消息队列发送函数OSTaskQPost()

函数 OSTaskQPost()用来发送任务消息队列，参数中有指向消息要发送给的任务控制块的指针，任何任务都可以发送消息给拥有任务消息队列的任务（任务在被创建的时候，要设置参数 q_size 大于 0）。

OSTaskQPost() 源码：

```c
#if OS_CFG_TASK_Q_EN > 0u                  //如果使能了任务消息队列
void  OSTaskQPost (OS_TCB       *p_tcb,    //目标任务
                   void         *p_void,   //消息内容地址
                   OS_MSG_SIZE   msg_size, //消息长度
                   OS_OPT        opt,      //选项
                   OS_ERR       *p_err)    //返回错误类型
{
    CPU_TS   ts;



#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                //如果使能了参数检测
    switch (opt) {                        //根据选项分类处理
        case OS_OPT_POST_FIFO:            //如果选项在预期内
        case OS_OPT_POST_LIFO:
        case OS_OPT_POST_FIFO | OS_OPT_POST_NO_SCHED:
        case OS_OPT_POST_LIFO | OS_OPT_POST_NO_SCHED:
             break;                       //直接跳出

        default:                          //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;  //错误类型为“选项非法”
             return;                      //返回，停止执行
    }
#endif

    ts = OS_TS_GET();                                  //获取时间戳

#if OS_CFG_ISR_POST_DEFERRED_EN > 0u                   //如果使能了中断延迟发布
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {         //如果该函数在中断中被调用
        OS_IntQPost((OS_OBJ_TYPE)OS_OBJ_TYPE_TASK_MSG, //将消息先发布到中断消息队列  
                    (void      *)p_tcb,
                    (void      *)p_void,
                    (OS_MSG_SIZE)msg_size,
                    (OS_FLAGS   )0,
                    (OS_OPT     )opt,
                    (CPU_TS     )ts,
                    (OS_ERR    *)p_err);
        return;                                         //返回
    }
#endif

    OS_TaskQPost(p_tcb,                                 //将消息直接发布
                 p_void,
                 msg_size,
                 opt,
                 ts,
                 p_err);
}
#endif
```

- 如果使能了中断延迟发布，并且如果该函数在中断中被调用，就先将消息先发布到中断消息队列。

- 调用 OS_TaskQPost() 函数将消息直接发送。



OS_TaskQPost() 源码：

```c
#if OS_CFG_TASK_Q_EN > 0u                   //如果使能了任务消息队列
void  OS_TaskQPost (OS_TCB       *p_tcb,    //目标任务
                    void         *p_void,   //消息内容地址
                    OS_MSG_SIZE   msg_size, //消息长度
                    OS_OPT        opt,      //选项
                    CPU_TS        ts,       //时间戳
                    OS_ERR       *p_err)    //返回错误类型
{
    CPU_SR_ALLOC();  //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
									   //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
									   // SR（临界段关中断只需保存SR），开中断时将该值还原。

    OS_CRITICAL_ENTER();                                   //进入临界段
    if (p_tcb == (OS_TCB *)0) {                            //如果 p_tcb 为空
        p_tcb = OSTCBCurPtr;                               //目标任务为自身
    }
   *p_err  = OS_ERR_NONE;                                  //错误类型为“无错误”
    switch (p_tcb->TaskState) {                            //根据任务状态分类处理
        case OS_TASK_STATE_RDY:                            //如果目标任务没等待状态
        case OS_TASK_STATE_DLY:
        case OS_TASK_STATE_SUSPENDED:
        case OS_TASK_STATE_DLY_SUSPENDED:
             OS_MsgQPut(&p_tcb->MsgQ,                      //把消息放入任务消息队列
                        p_void,
                        msg_size,
                        opt,
                        ts,
                        p_err);
             OS_CRITICAL_EXIT();                           //退出临界段
             break;                                        //跳出

        case OS_TASK_STATE_PEND:                           //如果目标任务有等待状态 
        case OS_TASK_STATE_PEND_TIMEOUT:
        case OS_TASK_STATE_PEND_SUSPENDED:
        case OS_TASK_STATE_PEND_TIMEOUT_SUSPENDED:
             if (p_tcb->PendOn == OS_TASK_PEND_ON_TASK_Q) {//如果等的是任务消息队列
                 OS_Post((OS_PEND_OBJ *)0,                 //把消息发布给目标任务
                         p_tcb,
                         p_void,
                         msg_size,
                         ts);
                 OS_CRITICAL_EXIT_NO_SCHED();              //退出临界段（无调度）
                 if ((opt & OS_OPT_POST_NO_SCHED) == (OS_OPT)0u) { //如果要调度任务
                     OSSched();                                    //调度任务
                 }
             } else {                                      //如果没在等待任务消息队列
                 OS_MsgQPut(&p_tcb->MsgQ,                  //把消息放入任务消息队列
                            p_void,                        
                            msg_size,
                            opt,
                            ts,
                            p_err);
                 OS_CRITICAL_EXIT();                      //退出临界段
             }
             break;                                       //跳出

        default:                                          //如果状态超出预期
             OS_CRITICAL_EXIT();                          //退出临界段
            *p_err = OS_ERR_STATE_INVALID;                //错误类型为“状态非法”
             break;                                       //跳出
    }
}
#endif
```

- 如果目标任务为空，则表示将任务消息释放给自己，那么 p_tcb 就指向当前任务。
- 如果目标任务没等待状态，就调用 OS_MsgQPut()函数将消息放入队列中，执行完毕就退出。
- 如果目标任务有等待状态，那就看是不是在等待任务消息队列，如果是的话，调用 OS_Post() 函数把任务消息发送给目标任务。
- 如果任务并不是在等待任务消息队列，那么调用 OS_MsgQPut() 函数将消息放入任务消息队列中即可。

任务消息队列的发送过程是跟消息队列发送过程差不多，先检查目标任务的状态，如果该任务刚刚好在等待任务消息队列的消息，那么直接让任务脱离等待状态即可。如果任务没有在等待任务消息队列的消息，那么就将消息插入到要发送消息的任务消息队列。 



OSTaskQPost() 使用实例：

```c
OS_ERR      err; 

/* 发布消息到任务 AppTaskPend */ 
OSTaskQPost ((OS_TCB      *)&AppTaskPendTCB,              //目标任务的控制块 
             (void        *)"YeHuo uCOS-III",             //消息内容 
             (OS_MSG_SIZE  )sizeof ( "YeHuo uCOS-III" ),  //消息长度 
             (OS_OPT       )OS_OPT_POST_FIFO,   
             //发布到任务消息队列的入口端 
             (OS_ERR      *)&err);                        //返回错误类型
```



### 任务消息队列获取函数OSTaskQPend()

与 OSTaskQPost()任务消息队列发送函数相对应，OSTaskQPend()函数用于获取一个任务消息队列，函数的参数中没有指定哪个任务获取任务消息，实际上就是当前执行的任务，当任务调用了这个函数就表明这个任务需要获取任务消息。

OSTaskQPend() 源码：

```c
#if OS_CFG_TASK_Q_EN > 0u                     //如果使能了任务消息队列
void  *OSTaskQPend (OS_TICK       timeout,    //等待期限（单位：时钟节拍）
                    OS_OPT        opt,        //选项
                    OS_MSG_SIZE  *p_msg_size, //返回消息长度
                    CPU_TS       *p_ts,       //返回时间戳
                    OS_ERR       *p_err)      //返回错误类型
{
    OS_MSG_Q     *p_msg_q;
    void         *p_void;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return ((void *)0);             //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u          //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) {  //如果该函数在中断中被调用
       *p_err = OS_ERR_PEND_ISR;                //错误类型为“在中断中中止等待”
        return ((void *)0);                     //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                   //如果使能了参数检测
    if (p_msg_size == (OS_MSG_SIZE *)0) {    //如果 p_msg_size 为空
       *p_err = OS_ERR_PTR_INVALID;          //错误类型为“指针不可用”
        return ((void *)0);                  //返回0（有错误），停止执行
    }
    switch (opt) {                           //根据选项分类处理
        case OS_OPT_PEND_BLOCKING:           //如果选项在预期内
        case OS_OPT_PEND_NON_BLOCKING:
             break;                          //直接跳出

        default:                             //如果选项超出预期
            *p_err = OS_ERR_OPT_INVALID;     //错误类型为“选项非法”
             return ((void *)0);             //返回0（有错误），停止执行
    }
#endif

    if (p_ts != (CPU_TS *)0) {    //如果 p_ts 非空
       *p_ts  = (CPU_TS  )0;      //初始化（清零）p_ts，待用于返回时间戳
    }

    CPU_CRITICAL_ENTER();                                  //关中断
    p_msg_q = &OSTCBCurPtr->MsgQ;                          //获取当前任务的消息队列
    p_void  = OS_MsgQGet(p_msg_q,                          //从队列里获取一个消息
                         p_msg_size,
                         p_ts,
                         p_err);
    if (*p_err == OS_ERR_NONE) {                          //如果获取消息成功
#if OS_CFG_TASK_PROFILE_EN > 0u                        //如果使能了任务控制块的简况变量
        if (p_ts != (CPU_TS *)0) {                                         //如果 p_ts 
            OSTCBCurPtr->MsgQPendTime = OS_TS_GET() - *p_ts;               //非空，更新
            if (OSTCBCurPtr->MsgQPendTimeMax < OSTCBCurPtr->MsgQPendTime) {//等待任务消
                OSTCBCurPtr->MsgQPendTimeMax = OSTCBCurPtr->MsgQPendTime;  //息队列的最
            }                                                              //长时间记录。
        }
#endif
        CPU_CRITICAL_EXIT();                             //开中断 
        return (p_void);                                 //返回消息内容
    }
    /* 如果获取消息不成功（队列里没有消息） */
    if ((opt & OS_OPT_PEND_NON_BLOCKING) != (OS_OPT)0) { //如果选择了不堵塞任务
       *p_err = OS_ERR_PEND_WOULD_BLOCK;                 //错误类型为“缺乏阻塞”
        CPU_CRITICAL_EXIT();                             //开中断
        return ((void *)0);                              //返回0（有错误），停止执行
    } else {                                             //如果选择了堵塞任务
        if (OSSchedLockNestingCtr > (OS_NESTING_CTR)0) { //如果调度器被锁
            CPU_CRITICAL_EXIT();                         //开中断
           *p_err = OS_ERR_SCHED_LOCKED;                 //错误类型为“调度器被锁”
            return ((void *)0);                          //返回0（有错误），停止执行
        }
    }
    /* 如果调度器未被锁 */                                                       
    OS_CRITICAL_ENTER_CPU_EXIT();                        //锁调度器，重开中断
    OS_Pend((OS_PEND_DATA *)0,                           //阻塞当前任务，等待消息 
            (OS_PEND_OBJ  *)0,
            (OS_STATE      )OS_TASK_PEND_ON_TASK_Q,
            (OS_TICK       )timeout);
    OS_CRITICAL_EXIT_NO_SCHED();                         //解锁调度器（无调度）

    OSSched();                                           //调度任务
    /* 当前任务（获得消息队列的消息）得以继续运行 */
    CPU_CRITICAL_ENTER();                                //关中断
    switch (OSTCBCurPtr->PendStatus) {                   //根据任务的等待状态分类处理
        case OS_STATUS_PEND_OK:                          //如果任务已成功获得消息
             p_void      = OSTCBCurPtr->MsgPtr;          //提取消息内容地址
            *p_msg_size  = OSTCBCurPtr->MsgSize;         //提取消息长度
             if (p_ts != (CPU_TS *)0) {                  //如果 p_ts 非空
                *p_ts  = OSTCBCurPtr->TS;                //获取任务等到消息时的时间戳
#if OS_CFG_TASK_PROFILE_EN > 0u                          //如果使能了任务控制块的简况变量
                OSTCBCurPtr->MsgQPendTime = OS_TS_GET() - OSTCBCurPtr->TS;     //更新等待
                if (OSTCBCurPtr->MsgQPendTimeMax < OSTCBCurPtr->MsgQPendTime) {//任务消息
                    OSTCBCurPtr->MsgQPendTimeMax = OSTCBCurPtr->MsgQPendTime;  //队列的最
                }                                                              //长时间记
#endif                                                                         //录。
             }
            *p_err = OS_ERR_NONE;                        //错误类型为“无错误”
             break;                                      //跳出

        case OS_STATUS_PEND_ABORT:                       //如果等待被中止
             p_void     = (void      *)0;                //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                //返回消息大小为0
             if (p_ts  != (CPU_TS *)0) {                 //如果 p_ts 非空
                *p_ts   = (CPU_TS  )0;                   //清零 p_ts
             }
            *p_err      =  OS_ERR_PEND_ABORT;            //错误类型为“等待被中止”
             break;                                      //跳出

        case OS_STATUS_PEND_TIMEOUT:                     //如果等待超时，
        default:                                         //或者任务状态超出预期。
             p_void     = (void      *)0;                //返回消息内容为空
            *p_msg_size = (OS_MSG_SIZE)0;                //返回消息大小为0
             if (p_ts  != (CPU_TS *)0) {                 //如果 p_ts 非空
                *p_ts   =  OSTCBCurPtr->TS;
             }
            *p_err      =  OS_ERR_TIMEOUT;               //错误类为“等待超时”
             break;                                      //跳出
    }
    CPU_CRITICAL_EXIT();                                 //开中断
    return (p_void);                                     //返回消息内容地址
}
#endif
```

- 如果调度器未被锁，系统会锁调度器，重开中断。
- 调用 OS_Pend()函数将当前任务脱离就绪列表，并根据用户指定的阻塞时间插入到节拍列表，但是不会插入队列等待列表，然后打开调度器，但不进行调度。
- 如果任务状态是 OS_STATUS_PEND_OK，则表示任务获取到消息了，那么就从任务控制块中提取消息，这是因为在发送消息给任务的时候，会将消息放入任务控制块的 MsgPtr 成员变量中，然后继续提取消息大小，如果 p_ts 非空，记录获取任务等到消息时的时间戳，返回错误类型为“无错误”的错误代码，跳出 switch 语句。
- 如果任务在等待（阻塞）中被中止，则返回消息内容为空，返回消息大小为 0，返回错误类型为“等待被中止”的错误代码，跳出 switch 语句。
- 如果任务等待（阻塞）超时，说明等待的时间过去了，任务也没获取到消息，则返回消息内容为空，返回消息大小为 0，返回错误类型为“等待超时”的错误代码，跳出 switch 语句。



OSTaskQPend() 使用实例：

```c
char * pMsg;
OS_ERR         err;
OS_MSG_SIZE    msg_size; 
CPU_TS         ts;
pMsg = OSTaskQPend ((OS_TICK        )0,                    //无期限等待
                    (OS_OPT         )OS_OPT_PEND_BLOCKING, //没有消息就阻塞任务
                    (OS_MSG_SIZE   *)&msg_size,            //返回消息长度
                    (CPU_TS        *)&ts,                  //返回消息被发送的时间戳
                    (OS_ERR        *)&err);                //返回错误类型
```



# 内存管理

## 1. 内存管理的基本概念

在嵌入式系统设计中，内存分配应该是根据所设计系统的特点来决定选择使用动态内存分配还是静态内存分配算法，一些可靠性要求非常高的系统应选择使用静态的，而普通的业务系统可以使用动态来提高内存使用效率。**静态可以保证设备的可靠性但是需要考虑内存上限，内存使用效率低，而动态则是相反**。

uCOS 的内存管理是采用**「内存池」**的方式进行管理，也就是创建一个内存池，**静态划分一大块连续空间作为内存管理的空间**，里面划分为很多个内存块，我们在使用的时候就从这个内存池中获取一个内存块，使用完毕的时候用户可以将其放回内存池中，这样子就不会导致内存碎片的产生。uCOS 内存管理模块用于管理系统中内存资源，它是操作系统的核心模块之一，主要**包括内存池的创建、分配以及释放**。

在嵌入式实时操作系统中，调用 malloc() 和 free() 是危险的：

- 这些函数在小型嵌入式系统中并不总是可用的，小型嵌入式设备中的 RAM 不足。 
- 它们的**实现可能占据了相当大的代码空间**。
- 它们几乎都**不是安全的**。
- 它们并**不是确定的**，每次调用这些函数**「执行的时间可能都不一样」**。
- 它们有**「可能产生碎片」**。
- 这两个函数会使得链接器配置得复杂。
- 如果允许堆空间的生长方向覆盖其他变量占据的内存，它们会成为 debug 的灾难。

在一般的实时嵌入式系统中，由于实时性的要求，很少使用虚拟内存机制。**所有的内存都需要用户参与分配，直接操作物理内存，所分配的内存不能超过系统的物理内存，所有的系统堆栈的管理，都由用户自己管理**。

同时，在嵌入式实时操作系统中，对内存的分配时间要求更为苛刻，**分配内存的时间必须是确定的**。一般内存管理算法是根据需要存储的数据的长度在内存中去寻找一个与这段数据相适应的空闲内存块，然后将数据存储在里面，而寻找这样一个空闲内存块所耗费的时间是不确定的，因此对于实时系统来说，这就是不可接受的，**实时系统必须要保证内存块的分配过程在可预测的确定时间内完成，否则实时任务对外部事件的响应也将变得不可确定**。

uCOS 提供的内存分配算法是**「只允许用户分配固定大小的内存块」**，当使用完成就将其放回内存池中，这样子**「分配效率极高，时间复杂度是 O(1)」**，也就是一个固定的时间常数，并不会因为系统内存的多少而增加遍历内存块列表的时间，并且还**「不会导致内存碎片」**的出现，但是这样的内存分配机制**「会导致内存利用率的下降以及申请内存大小的限制」**。 



## 2. 内存管理的运作机制

内存池（Memory Pool）是一种用于分配大量大小相同的内存对象的技术，它可以极大加快内存分配/释放的速度。 

在系统**编译的时候**，编译器就静态划分了一个大数组作为系统的内存池，然后**在初始化的时候将其分成大小相等的多个内存块，内存块直接通过链表连接起来（此链表也称为空闲内存块列表）**。每次**分配的时候，从空闲内存块列表中取出表头上第一个内存块，提供给申请者**。物理内存中允许存在多个大小不同的内存池，每一个内存池又由多个大小相同的空闲内存块组成。

必须先创建内存池才能去使用内存池里面的内存块，**在创建的时候，必须定义一个内存池控制块**，然后进行相关初始化，内存控制块的参数包括内存池名称，内存池起始地址，内存块大小，内存块数量等信息，在以后需要从内存池取出内存块或者释放内存块的时候，只需根据内存控制块的信息就能很轻易做到。

内存控制块 os_mem：

```c
struct os_mem {                                             /* MEMORY CONTROL BLOCK */
    OS_OBJ_TYPE          Type;                              /* 内核对象类型 OS_OBJ_TYPE_MEM */
    void                *AddrPtr;                           /* 内存池的起始地址 */
    CPU_CHAR            *NamePtr;
    void                *FreeListPtr;                       /* 空闲内存块列表 */
    OS_MEM_SIZE          BlkSize;                           /* 内存块大小 */
    OS_MEM_QTY           NbrMax;                            /* 内存池中内存块的总数量 */
    OS_MEM_QTY           NbrFree;                           /* 空闲内存块数量 */
#if OS_CFG_DBG_EN > 0u
    OS_MEM              *DbgPrevPtr;
    OS_MEM              *DbgNextPtr;
#endif
};
```



静态内存示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626160225.png" width="700px" /> </div>

注意：内存池中的内存块是通过单链表连接起来的，类似于消息池，内存池在创建的时候内存块地址是连续的，但是经过多次申请以及释放后，空闲内存块列表的内存块在地址上不一定是连续的。



## 3. 内存管理的应用场景

内存管理的主要工作是**「动态划分并管理用户分配好的内存区间」**，主要是**「在用户需要使用大小不等的内存块的场景中使用」**，当用户需要分配内存时，可以通过操作系统的内存申请函数索取指定大小内存块，一旦使用完毕，通过动态内存释放函数归还所占用内存，使之**「可以重复使用」**（heap_1.c 的内存管理除外）。

例如我们需要定义一个 float 型数组：floatArr[]; 

但是，在使用数组的时候，总有一个问题困扰着我们：数组应该有多大？在很多的情况下，你并**不能确定要使用多大的数组**，可能为了避免发生错误你就需要把数组定义得足够大。即使你知道想利用的空间大小，但是如果因为某种特殊原因空间利用的大小有增加或者减少，你又必须重新去修改程序，扩大数组的存储范围。这种分配固定大小的内存分配方法称之为静态内存分配。这种内存分配的方法存在比较严重的缺陷，在大多数情况下会浪费大量的内存空间，在少数情况下，当你定义的数组不够大时，可能引起下标越界错误，甚至导致严重后果。

uCOS 将系统静态分配的大数组作为内存池，然后进行内存池的初始化，然后分配固定大小的内存块。

注意：uCOS 也不能很好解决这种问题，因为内存块的大小是固定的，**「无法解决这种弹性很大的内存需求」**，只能按照最大的内存块进行分配。但是 **「uCOS 的内存分配能解决内存利用率的问题」**，在**不需要使用内存的时候，将内存释放到内存池中，让其他任务能正常使用该内存块**。



## 4. 内存管理函数接口

### 内存池创建函数OSMemCreate()

在使用内存池的时候首先要创建一个内存池，需要用户静态分配一个数组空间作为系统的内存池，且用户还需定义一个内存控制块。创建内存池后，任务才可以通过系统的内存申请、释放函数从内存池中申请或释放内存。

OSMemCreate() 源码：

```c
void  OSMemCreate (OS_MEM       *p_mem,    //内存分区控制块
                   CPU_CHAR     *p_name,   //命名内存分区
                   void         *p_addr,   //内存分区首地址
                   OS_MEM_QTY    n_blks,   //内存块数目
                   OS_MEM_SIZE   blk_size, //内存块大小（单位：字节）
                   OS_ERR       *p_err)    //返回错误类型
{
#if OS_CFG_ARG_CHK_EN > 0u      
    CPU_DATA       align_msk;
#endif
    OS_MEM_QTY     i;
    OS_MEM_QTY     loops;
    CPU_INT08U    *p_blk;
    void         **p_link;               //二级指针，存放指针的指针
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL                //如果使能了安全检测
    if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
        return;                          //返回，停止执行
    }
#endif

#ifdef OS_SAFETY_CRITICAL_IEC61508               //如果使能了安全关键
    if (OSSafetyCriticalStartFlag == DEF_TRUE) { //如果在调用OSSafetyCriticalStart()后创建
       *p_err = OS_ERR_ILLEGAL_CREATE_RUN_TIME;  //错误类型为“非法创建内核对象”
        return;                                  //返回，停止执行
    }
#endif

#if OS_CFG_CALLED_FROM_ISR_CHK_EN > 0u         //如果使能了中断中非法调用检测
    if (OSIntNestingCtr > (OS_NESTING_CTR)0) { //如果该函数是在中断中被调用
       *p_err = OS_ERR_MEM_CREATE_ISR;         //错误类型为“在中断中创建对象”
        return;                                //返回，停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                             //如果使能了参数检测
    if (p_addr == (void *)0) {                         //如果 p_addr 为空      
       *p_err   = OS_ERR_MEM_INVALID_P_ADDR;           //错误类型为“分区地址非法”
        return;                                        //返回，停止执行
    }
    if (n_blks < (OS_MEM_QTY)2) {                      //如果分区的内存块数目少于2
       *p_err = OS_ERR_MEM_INVALID_BLKS;               //错误类型为“内存块数目非法”
        return;                                        //返回，停止执行
    }
    if (blk_size < sizeof(void *)) {                   //如果内存块空间小于指针的
       *p_err = OS_ERR_MEM_INVALID_SIZE;               //错误类型为“内存空间非法”
        return;                                        //返回，停止执行
    }
    align_msk = sizeof(void *) - 1u;                   //开始检查内存地址是否对齐
    if (align_msk > 0u) {
        if (((CPU_ADDR)p_addr & align_msk) != 0u){     //如果分区首地址没对齐
           *p_err = OS_ERR_MEM_INVALID_P_ADDR;         //错误类型为“分区地址非法”
            return;                                    //返回，停止执行
        }
        if ((blk_size & align_msk) != 0u) {            //如果内存块地址没对齐     
           *p_err = OS_ERR_MEM_INVALID_SIZE;           //错误类型为“内存块大小非法”
            return;                                    //返回，停止执行
        }
    }
#endif
    /* 将空闲内存块串联成一个单向链表 */
    p_link = (void **)p_addr;                          //内存分区首地址转为二级指针 ★
    p_blk  = (CPU_INT08U *)p_addr;                     //首个内存块地址
    loops  = n_blks - 1u;
    for (i = 0u; i < loops; i++) {                     //将内存块逐个串成单向链表
        p_blk +=  blk_size;                            //下一内存块地址
       *p_link = (void  *)p_blk;                       //在当前内存块保存下一个内存块地址 ★
        p_link = (void **)(void *)p_blk;               //下一个内存块的地址转为二级指针 ★
    }
   *p_link             = (void *)0;                    //最后一个内存块指向空

    OS_CRITICAL_ENTER();                               //进入临界段
    p_mem->Type        = OS_OBJ_TYPE_MEM;              //设置对象的类型   
    p_mem->NamePtr     = p_name;                       //保存内存分区的命名     
    p_mem->AddrPtr     = p_addr;                       //存储内存分区的首地址     
    p_mem->FreeListPtr = p_addr;                       //初始化空闲内存块池的首地址 
    p_mem->NbrFree     = n_blks;                       //存储空闲内存块的数目   
    p_mem->NbrMax      = n_blks;                       //存储内存块的总数目
    p_mem->BlkSize     = blk_size;                     //存储内存块的空间大小  

#if OS_CFG_DBG_EN > 0u            //如果使能了调试代码和变量 
    OS_MemDbgListAdd(p_mem);      //将内存管理对象插入内存管理双向调试列表
#endif

    OSMemQty++;                   //内存管理对象数目加1

    OS_CRITICAL_EXIT_NO_SCHED();  //退出临界段（无调度）
   *p_err = OS_ERR_NONE;          //错误类型为“无错误”
}
```

- 如果内存池的内存块数目少于 2，返回错误类型为“内存块数目非法”错误代码。

- 如果内存块空间小于一个指针的大小（在 stm32 上是 4 字节），返回错误类型为“内存空间非法”的错误代码。

- 需要检查内存地址是否对齐，如果内存池首地址没对齐，返回错误类型为“内存池地址非法”的错误代码。

- 如果内存块地址没对齐，返回错误类型为“内存块大小非法”的错误代码。

- 「for (i = 0u; i < loops; i++)」将空闲内存块逐个连接成一个单向链表，根据内存块起始地址与内存块大小获取下一个内存块的地址，然后在当前内存块中保存下一个内存块的地址，再将下一个内存块的地址转为二级指针，将这些内存块连接成一个单链表，也就是空闲内存块链表。

  一个内存块的操作是先计算是下一个内存块的地址，因为**此时数组元素的地址是连续的**，所以开始的时候只要在前一个内存块的首地址加上内存块字节大小即可得到下一个内存块的首地址，然后把下一个内存块的首地址放在前一个内存块中，就将他们串起来了，如此循环反复即可串成空闲内存块列表。 

- 「*p_link             = (void *)0;」将最后一个内存块存储的地址为空，表示到达空闲内存块列表尾部。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626161703.png" width="500px" /> </div>

内存池创建完成示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626161752.png" width="700px" /> </div>

OSMemCreate() 使用实例：

```c
OS_MEM  mem;                    //声明内存管理对象 
uint8_t ucArray [ 3 ] [ 20 ];   //声明内存池大小 

OS_ERR      err; 
/* 创建内存管理对象 mem */ 
OSMemCreate ((OS_MEM      *)&mem,             //指向内存管理对象 
             (CPU_CHAR    *)"Mem For Test",   //命名内存管理对象 
             (void        *)ucArray,          //内存池的首地址 
             (OS_MEM_QTY   )3,                //内存池中内存块数目 
             (OS_MEM_SIZE  )20,               //内存块的字节数目 
             (OS_ERR      *)&err);            //返回错误类型
```



### 内存申请函数OSMemGet()

这个函数用于申请固定大小的内存块，**从指定的内存池中分配一个内存块给用户使用**，该内存块的大小在内存池初始化的时候就已经决定的。如果内存池中有可用的内存块，则从内存池的空闲内存块列表上取下一个内存块并且返回对应的内存地址；如果内存池中已经没有可用内存块，则返回 0 与对应的错误代码 OS_ERR_MEM_NO_FREE_BLKS。

OSMemGet() 源码：

```c
void  *OSMemGet (OS_MEM  *p_mem, //内存管理对象
                 OS_ERR  *p_err) //返回错误类型
{
    void    *p_blk;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL                //如果使能了安全检测
    if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
        return ((void *)0);              //返回0（有错误），停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                 //如果使能了参数检测
    if (p_mem == (OS_MEM *)0) {            //如果 p_mem 为空            
       *p_err  = OS_ERR_MEM_INVALID_P_MEM; //错误类型为“内存分区非法”
        return ((void *)0);                //返回0（有错误），停止执行
    }
#endif

    CPU_CRITICAL_ENTER();                    //关中断
    if (p_mem->NbrFree == (OS_MEM_QTY)0) {   //如果没有空闲的内存块
        CPU_CRITICAL_EXIT();                 //开中断
       *p_err = OS_ERR_MEM_NO_FREE_BLKS;     //错误类型为“没有空闲内存块”  
        return ((void *)0);                  //返回0（有错误），停止执行
    }
    p_blk              = p_mem->FreeListPtr; //如果还有空闲内存块，就获取它
    p_mem->FreeListPtr = *(void **)p_blk;    //调整空闲内存块指针
    p_mem->NbrFree--;                        //空闲内存块数目减1
    CPU_CRITICAL_EXIT();                     //开中断
   *p_err = OS_ERR_NONE;                     //错误类型为“无错误”
    return (p_blk);                          //返回获取到的内存块
}
```

- 判断一下内存池控制块中NbrFree 的值，如果没有空闲的内存块，就没法申请内存，保存错误类型为“没有空闲内存块”的错误代码，返回 0 表示没申请到内存块。 
- 如果内存池中还有空闲内存块，就获取它，获取的过程就是从空闲内存块中取出一个内存块，并且返回该内存块的地址。
- 调整内存池控制块的空闲内存块指针，指向下一个可用的内存块。

假设我们在内存池创建完成后就调用 OSMemGet()函数申请一个内存块，那么申请完毕后的内存块示意图如下，被申请出去的内存块会脱离空闲内存块列表，并且内存控制块中的 NbrFree 变量会减一。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626162132.png" width="700px" /> </div>



OSMemGet() 使用实例：

```c
OS_MEM  mem;                    //声明内存管理对象 
OS_ERR      err; 
/* 向 mem 获取内存块 */ 
p_mem_blk = OSMemGet ((OS_MEM      *)&mem,              //指向内存管理对象 
                      (OS_ERR      *)&err);             //返回错误类型 
```



### 内存释放函数OSMemPut()

嵌入式系统的内存对我们来说是十分珍贵的，任何内存块使用完后都必须被释放，否则会造成内存泄露，导致系统发生致命错误。uCOS 提供了 OSMemPut()函数进行内存的释放管理，使用该函数接口时，根据指定的内存控制块对象，将内存块插入内存池的空闲内存块列表中，然后增加该内存池的可用内存块数目。

OSMemPut() 源码：

```c
void  OSMemPut (OS_MEM  *p_mem,   //内存管理对象
                void    *p_blk,   //要退回的内存块
                OS_ERR  *p_err)   //返回错误类型
{
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

#ifdef OS_SAFETY_CRITICAL                //如果使能了安全检测
    if (p_err == (OS_ERR *)0) {          //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION();  //执行安全检测异常函数
        return;                          //返回，停止执行
    }
#endif

#if OS_CFG_ARG_CHK_EN > 0u                  //如果使能了参数检测
    if (p_mem == (OS_MEM *)0) {             //如果 p_mem 为空                
       *p_err  = OS_ERR_MEM_INVALID_P_MEM;  //错误类型为“内存分区非法”
        return;                             //返回，停止执行
    }
    if (p_blk == (void *)0) {               //如果内存块为空
       *p_err  = OS_ERR_MEM_INVALID_P_BLK;  //错误类型为"内存块非法"
        return;                             //返回，停止执行
    }
#endif

    CPU_CRITICAL_ENTER();                    //关中断
    if (p_mem->NbrFree >= p_mem->NbrMax) {   //如果内存池已满 ★            
        CPU_CRITICAL_EXIT();                 //开中断
       *p_err = OS_ERR_MEM_FULL;             //错误类型为“内存分区已满”
        return;                              //返回，停止执行
    }
    *(void **)p_blk    = p_mem->FreeListPtr; //把内存块插入空闲内存块链表 ★
    p_mem->FreeListPtr = p_blk;              //内存块退回到链表的最前端 ★
    p_mem->NbrFree++;                        //空闲内存块数目加1
    CPU_CRITICAL_EXIT();                     //开中断
   *p_err              = OS_ERR_NONE;        //错误类型为“无错误”
}
```

- 如果内存池已经满了，那是无法进行释放的，返回错误类型为“内存池已满”的错误代码。
- 如果内存池没满，那么释放内存块到内存池中，把内存块插入空闲内存块列表。 内存块退回到链表的最前端。

在释放一个内存块的时候，我们会将内存插入内存池中空闲内存块列表的**首部**，然后增加内存池中空闲内存块的数量。



OSMemPut() 使用实例：

```c
OS_MEM  mem;                    //声明内存管理对象 
OS_ERR      err; 

/* 释放内存块 */ 
OSMemPut ((OS_MEM  *)&mem,                        //指向内存管理对象 
          (void    *)pMsg,                        //内存块的首地址 
          (OS_ERR  *)&err);                       //返回错误类型 
```

**注意：OSMemCreate() 只能在任务级被调用，但是 OSMemGet() 和OSMemPut() 可以在中断中被调用。**



# 中断管理

## 1. 异常与中断的基本概念

异常是**导致处理器脱离正常运行转向执行特殊代码**的任何**事件**，如果不及时进行处理，轻则系统出错，重则会导致系统毁灭性瘫痪。所以正确地处理异常，避免错误的发生是提高软件鲁棒性（稳定性）非常重要的一环，对于实时系统更是如此。 

**「异常是指任何打断处理器正常执行，并且迫使处理器进入一个由有特权的特殊指令执行的事件」**。异常通常可以分成两类：**同步异常和异步异常**。

- 同步异常是指**由内部事件（像处理器指令运行产生的事件）引起的异常**，例如造成被零除的算术运算引发一个异常，又如在某些处理器体系结构中，对于确定的数据尺寸必须从内存的偶数地址进行读和写操作。从一个奇数内存地址的读或写操作将引起存储器存取一个错误事件并引起一个异常（称为校准异常）。
- 异步异常主要是指**由外部异常源产生的异常**，是一个由外部硬件装置产生的事件引起的异步异常。

同步异常和异步异常的区别：

- 同步异常不同于异步异常的地方是**事件的来源**，同步异常事件是由于执行某些指令而从处理器内部产生的，而异步异常事件的来源是外部硬件装置。例如按下设备某个按钮产生的事件。
- 同步异常与异步异常的区别还在于，同步异常触发后，系统**必须立刻进行处理**而不能够依然执行原有的程序指令步骤；而异步异常则**可以延缓处理甚至是忽略**，例如按键中断异常，虽然中断异常触发了，但是系统可以忽略它继续运行（同样也忽略了相应的按键事件）。

**「中断属于异步异常」**。所谓中断是**指中央处理器 CPU 正在处理某件事的时候，外部发生了某一事件，请求 CPU 迅速处理，CPU 暂时中断当前的工作，转入处理所发生的事件，处理完后，再回到原来被中断的地方，继续原来的工作，这样的过程称为中断**。「中断能打断任务的运行，无论该任务具有什么样的优先级」，因此中断一般用于处理比较紧急的事件，而且只做简单处理，例如标记该事件，在使用 uCOS 系统时，一般建议使用信号量、消息或事件标志组等标志中断的发生，将这些内核对象发布给处理任务，处理任务再做具体处理。 

通过中断机制，**在外设不需要 CPU 介入时，CPU 可以执行其他任务，而当外设需要 CPU 时通过产生中断信号使 CPU 立即停止当前任务转而来响应中断请求**。这样可以使CPU**「避免把大量时间耗费在等待、查询外设状态的操作上」**，因此将**「大大提高系统实时性以及执行效率」**。 

uCOS 源码中有许多处临界段的地方，**临界段虽然保护了关键代码的执行不被打断，但也会影响系统的实时，任何使用了操作系统的中断响应都不会比裸机快**。比如，某个时候有一个任务在运行中，并且该任务部分程序将中断屏蔽掉，也就是进入临界段中，这个时候如果有一个紧急的中断事件被触发，这个中断就会被挂起，不能得到及时响应，必须等到中断开启才可以得到响应，如果屏蔽中断时间超过了紧急中断能够容忍的限度，危害是可想而知的。操作系统的中断在某些时候会产生必要的中断延迟，因此**调用中断屏蔽函数进入临界段的时候，也需快进快出**。

UCOS 的中断管理支持： 

- 开/关中断
- 恢复中断
- 中断使能
- 中断屏蔽
- 中断嵌套
- 中断延迟发布



### 中断的介绍

与中断相关的硬件可以划分为三类：外设、中断控制器、CPU 本身。

- 外设：当外设需要请求 CPU 时，产生一个中断信号，该信号连接至中断控制器。
- 中断控制器：中断控制器是 **CPU 众多外设中的一个**，它一方面接收其他外设中断信号的输入，另一方面，它会发出中断信号给 CPU。可以通过对中断控制器编程实现对中断源的优先级、触发方式、打开和关闭源等设置操作。在 Cortex-M 系列控制器中常用的中断控制器是 **NVIC**（内嵌向量中断控制器 Nested Vectored Interrupt Controller）。 
- CPU：CPU 会响应中断源的请求，中断当前正在执行的任务，转而执行中断处理程序。NVIC 最多支持 240 个中断，每个中断最多 256 个优先级。 



### 和中断相关的名词解释

中断号：每个中断请求信号都会有特定的标志，使得计算机能够判断是哪个设备提出的中断请求，这个标志就是中断号。 

中断请求：“紧急事件” 需向 CPU 提出申请，要求 CPU 暂停当前执行的任务，转而处理该 “紧急事件”，这一过程称为中断请求。

中断优先级：为使系统能够及时响应并处理所有中断，系统根据中断时间的重要性和紧迫程度，将中断源分为若干个级别。

中断处理程序：当外设产生中断请求后，CPU 暂停当前的任务，转而响应中断申请，即执行中断处理程序。 

中断触发：中断源向 CPU 发出控制信号，将中断触发器置 “1”，表明该中断源产生了中断，要求 CPU 去响应该中断，CPU 暂停当前任务，执行相应的中断处理程序。中断触发类型：外部中断申请通过一个物理信号发送到 NVIC，可以是电平触发或边沿触发。

中断向量：**中断服务程序的入口地址**。

中断向量表：**存储中断向量的存储区**，中断向量与中断号对应，中断向量在中断向量表中按照中断号顺序存储。

临界段：代码的临界段也称为临界区，一旦这部分代码开始执行，则不允许任何中断打断。为确保临界段代码的执行不被中断，在进入临界段之前须关中断，而临界段代码执行完毕后，要立即开中断。 



## 2. 中断的运作机制

当中断产生时，处理机将按如下的顺序执行： 
1. 保存当前处理机状态信息 
2. 载入异常或中断处理函数到 PC 寄存器 
3. 把控制权转交给处理函数并开始执行 
4. 当处理函数执行完成时，恢复处理器状态信息 
5. 从异常或中断中返回到前一个程序执行点 

**中断使得 CPU 可以在事件发生时才给予处理，而不必让 CPU 连续不断地查询是否有相应的事件发生**。通过两条特殊指令：**关中断和开中断**可以让处理器不响应或响应中断，在关闭中断期间，通常处理器会把新产生的中断挂起，当中断打开时立刻进行响应，所以**会有适当的延时响应中断**，故用户在**进入临界区的时候应快进快出**。 

中断发生的环境有两种情况：在任务的上下文中，在中断服务函数处理上下文中。

- 任务在工作的时候，如果此时发生了一个中断，无论中断的优先级是多大，都会打断当前任务的执行，从而转到对应的中断服务函数中执行。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626210245.png" width="600px" /> </div>

​		(1)、(3)：在任务运行的时候发生了中断，那么中断会打断任务的运行，那么操作系统将先保存当前任务的上下文环境，转而		去处理中断服务函数。

​		(2)、(4)：当且仅当中断服务函数处理完的时候才恢复任务的上下文环境，继续运行任务。 

- 在执行中断服务例程的过程中，如果有更高优先级别的中断源触发中断，由于当前处于中断处理上下文环境中，根据不同的处理器构架可能有不同的处理方式，比如新的中断挂起直到当前中断处理离开后再进行响应；或新的高优先级中断打断当前中断处理过程，而去直接响应这个更高优先级的新中断源。后面这种情况，称之为**中断嵌套**。在硬实时环境中，前一种情况是不允许发生的，因为这样不能使响应中断的时间尽量的短。而在软实时环境上，**uCOS 允许中断嵌套，即在一个中断服务例程期间，处理器可以响应另外一个优先级更高的中断**。

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626210417.png" width="500px" /> </div>

​		(1)：当中断 1 的服务函数在处理的时候发生了中断 2，由于中断 2 的优先级比中断 1 更高，所以发生了中断嵌套，那么操作		系统将先保存当前中断服务函数的上下文，并且转向处理中断 2，当且仅当中断 2 执行完的时候 (2) 才能继续执行中断1。



## 3. 中断延迟的概念

即使操作系统的响应很快了，但对于中断的处理仍然存在着中断延迟响应的问题，我们称之为中断延迟(Interrupt Latency) 。中断延迟是**指从硬件中断发生到开始执行中断处理程序第一条指令之间的这段时间**。也就是：系统接收到中断信号到操作系统作出响应，并完成换到转入中断服务程序的时间也可以简单地理解为：（外部）硬件（设备）发生中断，到系统执行中断服务子程序
（ISR，interrupt service routine）的第一条指令的时间。 

中断的处理过程是：外界硬件发生了中断后，CPU 到中断处理器读取中断向量，并且查找中断向量表，找到对应的中断服务子程序（ISR）的首地址，然后跳转到对应的 ISR 去做相应处理。这部分时间，称之为**识别中断时间**。

在允许中断嵌套的实时操作系统中，中断也是基于优先级的，允许高优先级中断抢断正在处理的低优先级中断，所以，如果当前正在处理更高优先级的中断，即使此时有低优先级的中断，也系统不会立刻响应，而是等到高优先级的中断处理完之后，才会响应。而即使在不支持中断嵌套，即中断是没有优先级的，中断是不允许被中断的，所以，如果当前系统正在处理一个中断，而此时另一个中断到来了，系统也是不会立即响应的，而只是等处理完当前的中断之后，才会处理后来的中断。此部分时间，我称其为：**等待中断打开时间**。 

在操作系统中，很多时候我们会主动进入临界段，系统不允许当前状态被中断打断，故而在临界区发生的中断会被挂起，直到退出临界段时候打开中断。此部分时间称之为关闭中断时间。 

中断延迟可以定义为，从中断开始的时刻到中断服务例程开始执行的时刻之间的时间段。**中断延迟 = 识别中断时间 + [等待中断打开时间] + [关闭中断时间]**。 注意：“[ ]”的时间是不一定都存在的，此处为最大可能的中断延迟时间。

此外，中断恢复时间定义为：执行完 ISR 中最后一句代码后到恢复到任务级代码的这段时间。 任务延迟时间定义为：中断发生到恢复到任务级代码的这段时间。



## 4. 中断的应用场景

中断在嵌入式处理器中应用非常之多，没有中断的系统不是一个好系统，**因为有中断，才能启动或者停止某件事情，从而转去做另一间事情**。



## 5.  中断管理讲解

ARM Cortex-M 系列内核的中断是由硬件管理的，而 uCOS 是软件，它并不接管由硬件管理的相关中断（接管简单来说就是，所有的中断都由 RTOS 的软件管理，硬件来了中断时，由软件决定是否响应，可以挂起中断，延迟响应或者不响应），只支持简单的开关中断等，所以 **uCOS 中的中断使用其实跟裸机差不多的，需要我们自己配置中断，并且使能中断，编写中断服务函数**。在中断服务函数中使用内核 IPC 通信机制，一般**建议使用信号量、消息或事件标志组等标志事件的发生，将事件发布给处理任务，等退出中断后再由相关处理任务具体处理中断**，当然 uCOS 为了能让系统更快退出中断，它**支持中断延迟发布**，将中断级的发布变成任务级。 

ARM Cortex-M NVIC 支持中断嵌套功能：当一个中断触发并且系统进行响应时，处理器硬件会**将当前运行的部分上下文寄存器自动压入中断栈中**，这部分的寄存器包括 **PSR，R0，R1，R2，R3 以及 R12** 寄存器。当系统正在服务一个中断时，如果有一个更高优先级的中断触发，那么处理器同样的会打断当前运行的中断服务例程，然后把老的中断服务例程上下文的 PSR，R0，R1，R2，R3 和 R12 寄存器自动保存到中断栈中。这些部分上下文寄存器保存到中断栈的行为完全是硬件行为，这一点是与其他 ARM 处理器最大的区别（以往都需要依赖于软件保存上下文）。 

另外，在 ARM Cortex-M 系列处理器上，所有中断都采用**中断向量表**的方式进行处理，即当一个中断触发时，**处理器将直接判定是哪个中断源**，然后直接跳转到相应的固定位置进行处理。而在 ARM7、ARM9 中，一般是**先跳转进入 IRQ 入口**，然后**再由软件进行判断是哪个中断源触发**，获得了相对应的中断服务例程入口地址后，再进行后续的中断处理。ARM7、ARM9 的好处在于，所有中断它们都有统一的入口地址，便于 OS 的统一管理。而ARM Cortex-M 系列处理器则恰恰相反，每个中断服务例程必须排列在一起放在统一的地址上（这个地址必须要设置到 NVIC 的中断向量偏移寄存器中）。

uCOS 在 Cortex-M 系列处理器上也遵循与裸机中断一致的方法，当用户需要使用自定义的中断服务例程时，只需要定义相同名称的函数覆盖弱化符号（weak）即可。所以，uCOS 在Cortex-M 系列处理器的中断控制其实与裸机没什么差别，不过在进入中断与退出中断的时候需要调用一下 OSIntEnter() 函数与OSIntExit() 函数，方便中断嵌套管理。



## 6. 中断延迟发布

### 中断延迟发布的概念

uC/OS-III 有两种方法处理来自于中断的事件，直接发布（或者称为释放）和延迟发布。通过 os_cfg.h 中的 OS_CFG_ISR_POST_DEFERRED_EN 来选择，当设置为 0 时，uCOS 使用直接发布的方法。当设置为 1 时，使用延迟发布方法，用户可以根据自己设计系统的应用选择其中一种方法即可。

使能中断延时发布，**可以将中断级发布转换成任务级发布**，而且**「在进入临界段时也可以使用锁调度器代替关中断，这就大大减小了关中断时间，有利于提高系统的实时性（能实时响应中断而不受中断屏蔽导致响应延迟）」**。在前面提到的 OSTimeTick() 、
OSSemPost() 、 OSQPost() 、 OSFlagPost() 、 OSTaskSemPost() 、 OSTaskQPost() 、OSTaskSuspend()和 OSTaskResume() 等这些函数，如果没有使用中断延迟发布，那么调用这些函数意味着进入一段很长的临界段，也就要关中断很长时间。在使能中断延时发布后，如果在中断中调用这些函数，系统就会**将这些 post 提交函数必要的信息保存到中断延迟提交的变量中去**，为了配合中断延迟，μCOS 还将**创建优先级最高（优先级为 0）的任务——中断发布函数 OS_IntQTask，退出中断后根据之前保存的参数，在任务中再次进行 post 相关操作**。这个过程其实就是**「把中断中的临界段放到任务中来实现」**，这个时候进入临界段就可以用锁住调度器的方式代替关中断，因此大大减少了关中断的时间，系统将 post 操作延迟了，中断延迟就是这么来的。 

**进入临界段的方式可以是「关中断或者锁住调度器」，「系统中有些变量不可能在中断中被访问，所以只要保证其他任务不要使用这些变量即可，这个时候就可以用<锁调度启动>的方式，用锁住调度代替关中断，大大减少了关中断的时间，也能达到进入临界段的目的」**。中断延迟就是利用这种思想，让本该在中断中完成的事情切换到任务中完成，而且进入临界段的方式是锁定调度器，这样子中断就不会被屏蔽，系统能随时响应中断，并且，整个中断延迟发布的过程是不影响 post 的效果，因为 **uCOS 已经设定中断发布任务的优先级为最高，在退出中断后会马上进行 post 操作，这与在中断中直接进行 post 操作的时间基本一致**。 

注：操作系统内核相关函数一般为了保证其操作的完整性，一般都会进入或长或短的临界段，所以在中断的要尽量少调用内核函数，部分 μCOS 提供的函数是不允许在中断中调用的。 

在直接发布方式中，uCOS 访问临界段时是采用**关中断**方式。 然而，在延迟提交方式中，uCOS 访问临界段时是采用**锁调度器**方式。在延迟提交方式中，**访问中断队列时 uCOS 仍需要关中断进入临界段**，但是这段关中断时间是非常短的且是固定的。



### 中断延迟发布和直接发布的区别

中断延迟发布示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626213357.png" width="600px" /> </div>

(1)：进入中断，在中断中需要发布一个内核对象（如消息队列、信号量等），但是使用了中断延迟发布，在中断中值执行 OS_IntQPost() 函数，在这个函数中，采用关中断方式进入临界段，因此在这个时间段是不能响应中断的。 

(2)：已经将内核对象发布到中断消息队列，那么将唤醒 OS_IntQTask 任务，因为**该任务是最高优先级任务**，所以能立即被唤醒，然后转到 OS_IntQTask 任务中发布内核对象，在该任务中，调用 OS_IntQRePost() 函数进行发布内核对象，进入临界段的方式采
用锁调度器方式，那么**在这个阶段，中断是可以被响应的**。 

(3)：系统正常运行，任务按优先级进行切换。 



中断直接发布示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626213521.png" width="600px" /> </div>

(1)、(2)：采用中断直接发布的情况是在中断中直接屏蔽中断以进入临界段，**这段时间中，都不会响应中断**，直到发布完成，系统任务正常运行才开启中断。
(3)：系统正常运行，任务按照优先级正常切换从两个图中我们可以看出，很明显，**采用中断延迟发布的效果更好，将本该在中断中的处理转变成为在任务中处理，系统关中断的时间大大降低，使得系统能很好地响应外部中断**，如果在应用中关中断时间是关键性的，应用中有非常频繁的中断源，且应用不能接受直接发布方式那样较长的关中断时间，推荐使用中断延迟发布方式。 



### 中断队列控制块

如果使能中断延迟发布，在中断中调用内核对象发布（释放）函数，系统会将发布的内容存放在中断队列控制块中。

```c
#if OS_CFG_ISR_POST_DEFERRED_EN > 0u
struct  os_int_q {
    OS_OBJ_TYPE          Type;      /* 内核对象类型  */
    OS_INT_Q            *NextPtr;   /* 指向下一个中断队列控制块 */
    void                *ObjPtr;    /* 指向内核对象变量指针 */
    void                *MsgPtr;    /* 指向发布消息的指针 */
    OS_MSG_SIZE          MsgSize;   /* 记录发布的消息的字节大小 */
    OS_FLAGS             Flags;     /* 事件的标志位 */
    OS_OPT               Opt;       /* 记录发布内核对象时的选项 */
    CPU_TS               TS;        /* 记录时间戳 */
};
#endif
```



### 中断延迟发布任务初始化OS_IntQTaskInit()

在系统初始化的时候，如果我们使能了中断延迟发布，那么系统会根据我们自定义配置中断延迟发布任务的宏定义OS_CFG_INT_Q_SIZE 与 OS_CFG_INT_Q_TASK_STK_SIZE 进行相关初始化，这两个宏定义在 os_cfg_app.h 文件中。

OS_IntQTaskInit() 源码：

```c
void  OS_IntQTaskInit (OS_ERR  *p_err) 
{ 
    OS_INT_Q      *p_int_q; 
    OS_INT_Q      *p_int_q_next; 
    OS_OBJ_QTY     i; 

    #ifdef OS_SAFETY_CRITICAL 
    if (p_err == (OS_ERR *)0) 
    { 
        OS_SAFETY_CRITICAL_EXCEPTION(); 
        return; 
    } 
    #endif 

    /* 清空延迟提交过程中溢出的计数值 */ 
    OSIntQOvfCtr = (OS_QTY)0u; 

    //延迟发布信息队列的基地址必须不为空指针 
    if (OSCfg_IntQBasePtr == (OS_INT_Q *)0) (1) 
    { 
        *p_err = OS_ERR_INT_Q; 
        return; 
    } 

    //延迟发布队列成员必须不小于 2 个 
    if (OSCfg_IntQSize < (OS_OBJ_QTY)2u) (2) 
    { 
        *p_err = OS_ERR_INT_Q_SIZE; 
        return; 
    } 

    //初始化延迟发布任务每次运行的最长时间记录变量 
    OSIntQTaskTimeMax = (CPU_TS)0;  

    //将定义的数据连接成一个单向链表
    p_int_q = OSCfg_IntQBasePtr; (3) 
    p_int_q_next      = p_int_q; 
    p_int_q_next++; 
    for (i = 0u; i < OSCfg_IntQSize; i++)  
    { 
        //每个信息块都进行初始化 
        p_int_q->Type    =  OS_OBJ_TYPE_NONE; 
        p_int_q->ObjPtr  = (void      *)0; 
        p_int_q->MsgPtr  = (void      *)0; 
        p_int_q->MsgSize = (OS_MSG_SIZE)0u; 
        p_int_q->Flags   = (OS_FLAGS   )0u; 
        p_int_q->Opt     = (OS_OPT     )0u; 
        p_int_q->NextPtr = p_int_q_next; 
        p_int_q++; 
        p_int_q_next++; 
    }  
    //将单向链表的首尾相连组成一个“圈 
    p_int_q--; 
    p_int_q_next        = OSCfg_IntQBasePtr; 
    p_int_q->NextPtr = p_int_q_next; (4) 

    //队列出口和入口都指向第一个 
    OSIntQInPtr         = p_int_q_next; 
    OSIntQOutPtr = p_int_q_next; (5) 

    //清空延迟发布队列中需要进行发布的内核对象个数 
    OSIntQNbrEntries    = (OS_OBJ_QTY)0u; 
    //清空延迟发布队列中历史发布的内核对象最大个数 
    OSIntQNbrEntriesMax = (OS_OBJ_QTY)0u; 


    if (OSCfg_IntQTaskStkBasePtr == (CPU_STK *)0) 
    { 
        *p_err = OS_ERR_INT_Q_STK_INVALID; 
        return; 
    } 

    if (OSCfg_IntQTaskStkSize < OSCfg_StkSizeMin) 
    { 
        *p_err = OS_ERR_INT_Q_STK_SIZE_INVALID; 
        return; 
    } 
    //创建延迟发布任务 
    OSTaskCreate((OS_TCB     *)&OSIntQTaskTCB, 
                 (CPU_CHAR   *)((void *)"uC/OS-III ISR Queue Task"), 
                 (OS_TASK_PTR )OS_IntQTask, 
                 (void       *)0, 
                 (OS_PRIO     )0u,            //优先级最高 
                 (CPU_STK    *)OSCfg_IntQTaskStkBasePtr, 
                 (CPU_STK_SIZE)OSCfg_IntQTaskStkLimit, 
                 (CPU_STK_SIZE)OSCfg_IntQTaskStkSize, 
                 (OS_MSG_QTY  )0u, 
                 (OS_TICK     )0u, 
                 (void       *)0, 
                 (OS_OPT      )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR), 
                 (OS_ERR *)p_err); (6) 
} 

#endif 
```

- 延迟发布信息队列的基地址必须不为空指针，uCOS 在编译的时候就已经静态分配一个存储的空间（大数组）。

中断延迟发布队列存储空间（位于os_cfg_app.c）：

```c
#if (OS_CFG_ISR_POST_DEFERRED_EN > 0u) 
OS_INT_Q       OSCfg_IntQ          [OS_CFG_INT_Q_SIZE]; 
CPU_STK        OSCfg_IntQTaskStk   [OS_CFG_INT_Q_TASK_STK_SIZE]; 
#endif 

OS_INT_Q     * const  OSCfg_IntQBasePtr      = (OS_INT_Q   *)&OSCfg_IntQ[0]; 
OS_OBJ_QTY     const  OSCfg_IntQSize         = (OS_OBJ_QTY  )OS_CFG_INT_Q_SIZE; 
```

- 延迟发布队列成员（OSCfg_IntQSize  = OS_CFG_INT_Q_SIZE）必须不小于 2 个，该宏在 os_cfg_app.h 文件中定义。 
- 将定义的数据连接成一个单向链表，并且初始化每一个信息块的内容。  
- 将单向链表的首尾相连组成一个“圈”，环形单链表，处理完成
- 队列出口和入口都指向第一个信息块。
- 创建延迟发布任务，任务的优先级是 0，是最高优先级任务不允许用户修改。



中断延迟发布队列初始化完成示意图：

<div align="center"> <img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200626214755.png" width="650px" /> </div>



### 中断延迟发布过程OS_IntQPost()

如果使能了中断延迟发布，并且发送消息的函数是在中断中被调用，此时就不该立即发送消息，而是将消息的发送放在指定发布任务中，此时系统就将消息发布到中断消息队列中，等待到中断发布任务唤醒再发送消息。

OS_IntQPost() 源码：

```c
void  OS_IntQPost (OS_OBJ_TYPE   type,        //内核对象类型
                   void         *p_obj,       //被发布的内核对象
                   void         *p_void,      //消息队列或任务消息
                   OS_MSG_SIZE   msg_size,    //消息的数目
                   OS_FLAGS      flags,       //事件标志组
                   OS_OPT        opt,         //发布内核对象时的选项
                   CPU_TS        ts,          //发布内核对象时的时间戳
                   OS_ERR       *p_err)       //返回错误类型
{
    CPU_SR_ALLOC();  //使用到临界段（在关/开中断时）时必需该宏，该宏声明和定义一个局部变
                     //量，用于保存关中断前的 CPU 状态寄存器 SR（临界段关中断只需保存SR）
                     //，开中断时将该值还原。 

#ifdef OS_SAFETY_CRITICAL               //如果使能（默认禁用）了安全检测
    if (p_err == (OS_ERR *)0) {         //如果错误类型实参为空
        OS_SAFETY_CRITICAL_EXCEPTION(); //执行安全检测异常函数
        return;                         //返回，不继续执行
    }
#endif

    CPU_CRITICAL_ENTER();                                   //关中断
    if (OSIntQNbrEntries < OSCfg_IntQSize) {                //如果中断队列未占满   
        OSIntQNbrEntries++;

        if (OSIntQNbrEntriesMax < OSIntQNbrEntries) {       //更新中断队列的最大使用数目的历史记录
            OSIntQNbrEntriesMax = OSIntQNbrEntries;
        }
        /* 将要重新提交的内核对象的信息放入到中断队列入口的信息记录块 */
        OSIntQInPtr->Type       = type;                     //保存内核对象类型
        OSIntQInPtr->ObjPtr     = p_obj;                    //保存被发布的内核对象
        OSIntQInPtr->MsgPtr     = p_void;                   //保存消息内容指针
        OSIntQInPtr->MsgSize    = msg_size;                 //保存消息大小
        OSIntQInPtr->Flags      = flags;                    //保存事件标志组
        OSIntQInPtr->Opt        = opt;                      //保存选项
        OSIntQInPtr->TS         = ts;                       //保存对象被发布的时间错

        OSIntQInPtr             =  OSIntQInPtr->NextPtr;    //指向下一个带处理成员
        /* 让中断队列管理任务 OSIntQTask 就绪 */
        OSRdyList[0].NbrEntries = (OS_OBJ_QTY)1;            //更新就绪列表上的优先级0的任务数为1个 
        OSRdyList[0].HeadPtr    = &OSIntQTaskTCB;           //该就绪列表的头指针指向 OSIntQTask 任务
        OSRdyList[0].TailPtr    = &OSIntQTaskTCB;           //该就绪列表的尾指针指向 OSIntQTask 任务
        OS_PrioInsert(0u);                                  //在优先级列表中增加优先级0
        if (OSPrioCur != 0) {                               //如果当前运行的不是 OSIntQTask 任务
            OSPrioSaved         = OSPrioCur;                //保存当前任务的优先级
        }

       *p_err                   = OS_ERR_NONE;              //返回错误类型为“无错误”
    } else {                                                //如果中断队列已占满
        OSIntQOvfCtr++;                                     //中断队列溢出数目加1
       *p_err                   = OS_ERR_INT_Q_FULL;        //返回错误类型为“无错误”
    }
    CPU_CRITICAL_EXIT();                                    //开中断
}
```

- OSIntQNbrEntries 用于记录中断队列的入队数量，需要加一表示当前有信息记录块入队。 
- 将要重新提交的内核对象的信息放入到中断队列的信息记录块中，记录的信息有发布的对象类型、发布的内核对象、要发布的消息、要发布的消息大小、要发布的事件、选项、时间戳等信息。 
- 让中断队列管理任务 OSIntQTask 就绪，更新就绪列表上的优先级 0 的任务数为 1 个。
- 就绪列表的头尾指针都指向OSIntQTask 任务。
- 调用 OS_PrioInsert()函数在优先级列表中增加优先级0。
- 如果当前运行的不是 OS_IntQTask 任务，则需要保存当前任务的优先级。 
- 如果中断队列已占满，记录一下中断队列溢出数目，返回错误类型为“中断队列已满”的错误代码。 



OSTaskSemPost() 使用实例：

实现一个串口的 DMA 传输+空闲中断功能，当串口接收完不定长的数据之后产生一个空闲中断，在中断中将信号量传递给任务，任务在收到信号量的时候将串口的数据读取出来并且在串口调试助手中回显，中断服务函数则需要我们自己编写，并且中断被触发的时候（中断服务函数中）通过信号量告知任务。

```c
/**
  * @brief  USART 中断服务函数
  * @param  无
  * @retval 无
  */	
void macUSART_INT_FUN(void)
{
    OS_ERR   err;
    OSIntEnter(); 	                                     //进入中断

    if ( USART_GetITStatus ( macUSARTx, USART_IT_IDLE ) != RESET )
    {
        DMA_Cmd(USART_RX_DMA_CHANNEL, DISABLE);   

        USART_ReceiveData ( macUSARTx );  /* 清除标志位 */

        // 清DMA标志位
        DMA_ClearFlag( DMA1_FLAG_TC5 );          
        //  重新赋值计数值，必须大于等于最大可能接收到的数据帧数目
        USART_RX_DMA_CHANNEL->CNDTR = USART_RBUFF_SIZE;    
        DMA_Cmd(USART_RX_DMA_CHANNEL, ENABLE);     

        //给出信号量 ，发送接收到新数据标志，供前台程序查询

        /* 发送任务信号量到任务 AppTaskKey */
        OSTaskSemPost((OS_TCB  *)&AppTaskUsartTCB,   //目标任务
                      (OS_OPT   )OS_OPT_POST_NONE, //没选项要求
                      (OS_ERR  *)&err);            //返回错误类型		

    }
    OSIntExit();	                                       //退出中断
}
```



### 中断延迟发布任务OS_IntQTask()

在中断中将消息放入中断队列，那么接下来又怎么样进行发布内核对象呢？uCOS 在中断中只是将要提交的内核对象的信息都暂时保存起来，然后就绪优先级最高的中断延迟发布任务，接着继续执行中断，在退出所有中断嵌套后，第一个执行的任务就是
延迟发布任务。

OS_IntQTask() 源码：

```c
void  OS_IntQTask (void  *p_arg)
{
    CPU_BOOLEAN  done;
    CPU_TS       ts_start;
    CPU_TS       ts_end;
    CPU_SR_ALLOC(); //使用到临界段（在关/开中断时）时必需该宏，该宏声明和
                    //定义一个局部变量，用于保存关中断前的 CPU 状态寄存器
                    // SR（临界段关中断只需保存SR），开中断时将该值还原。

    p_arg = p_arg;                                          
    while (DEF_ON) {                                        //进入死循环
        done = DEF_FALSE;
        while (done == DEF_FALSE) {
            CPU_CRITICAL_ENTER();                           //关中断
            if (OSIntQNbrEntries == (OS_OBJ_QTY)0u) {       //如果中断队列里的内核对象发布完毕
                OSRdyList[0].NbrEntries = (OS_OBJ_QTY)0u;   //从就绪列表移除中断队列管理任务 OS_IntQTask
                OSRdyList[0].HeadPtr    = (OS_TCB   *)0;
                OSRdyList[0].TailPtr    = (OS_TCB   *)0;
                OS_PrioRemove(0u);                          //从优先级表格移除优先级0
                CPU_CRITICAL_EXIT();                        //开中断
                OSSched();                                  //任务调度
                done = DEF_TRUE;                            //退出循环
            } else {                                        //如果中断队列里还有内核对象
                CPU_CRITICAL_EXIT();                        //开中断
                ts_start = OS_TS_GET();                     //获取时间戳
                OS_IntQRePost();                            //发布中断队列里的内核对象
                ts_end   = OS_TS_GET() - ts_start;          //计算该次发布时间
                if (OSIntQTaskTimeMax < ts_end) {           //更新中断队列发布内核对象的最大时间的历史记录
                    OSIntQTaskTimeMax = ts_end;
                }
                CPU_CRITICAL_ENTER();                       //关中断
                OSIntQOutPtr = OSIntQOutPtr->NextPtr;       //中断队列出口转至下一个
                OSIntQNbrEntries--;                         //中断队列的成员数目减1
                CPU_CRITICAL_EXIT();                        //开中断
            }
        }
    }
}
```

- 如果中断队列里的内核对象发布完毕（OSIntQNbrEntries 变量的值为 0），从就绪列表移除中断延迟发布任务 OS_IntQTask，这样子的操作相当于挂起OS_IntQTask 任务。 
- 从优先级表格中移除优先级 0 的任务。
- 进行一次任务调度，这就保证了从中断出来后如果需要发布会将相应的内核对象全部进行发布直到全部都发布完成，才会进行一次任务调度，然后让其他的任务占用 CPU。 
- 如果中断队列里还存在未发布的 内核对象，就调用OS_IntQRePost()函数发布中断队列里的内核对象，其实这个函数才是真正的发布操作。
- 处理下一个要发布的内核对象，直到没有任何要发布的内核对象为止。



OS_IntQRePost() 源码：

```c
void  OS_IntQRePost (void)
{
    CPU_TS  ts;
    OS_ERR  err;


    switch (OSIntQOutPtr->Type) {   //根据内核对象类型分类处理
        case OS_OBJ_TYPE_FLAG:      //如果对象类型是事件标志
#if OS_CFG_FLAG_EN > 0u             //如果使能了事件标志，则发布事件标志
             (void)OS_FlagPost((OS_FLAG_GRP *) OSIntQOutPtr->ObjPtr,
                               (OS_FLAGS     ) OSIntQOutPtr->Flags,
                               (OS_OPT       ) OSIntQOutPtr->Opt,
                               (CPU_TS       ) OSIntQOutPtr->TS,
                               (OS_ERR      *)&err);
#endif
             break;                 //跳出

        case OS_OBJ_TYPE_Q:         //如果对象类型是消息队列
#if OS_CFG_Q_EN > 0u                //如果使能了消息队列，则发布消息队列
             OS_QPost((OS_Q      *) OSIntQOutPtr->ObjPtr,
                      (void      *) OSIntQOutPtr->MsgPtr,
                      (OS_MSG_SIZE) OSIntQOutPtr->MsgSize,
                      (OS_OPT     ) OSIntQOutPtr->Opt,
                      (CPU_TS     ) OSIntQOutPtr->TS,
                      (OS_ERR    *)&err);
#endif
             break;                 //跳出

        case OS_OBJ_TYPE_SEM:       //如果对象类型是多值信号量
#if OS_CFG_SEM_EN > 0u              //如果使能了多值信号量，则发布多值信号量
             (void)OS_SemPost((OS_SEM *) OSIntQOutPtr->ObjPtr,
                              (OS_OPT  ) OSIntQOutPtr->Opt,
                              (CPU_TS  ) OSIntQOutPtr->TS,
                              (OS_ERR *)&err);
#endif
             break;                 //跳出

        case OS_OBJ_TYPE_TASK_MSG:  //如果对象类型是任务消息
#if OS_CFG_TASK_Q_EN > 0u           //如果使能了任务消息，则发布任务消息
             OS_TaskQPost((OS_TCB    *) OSIntQOutPtr->ObjPtr,
                          (void      *) OSIntQOutPtr->MsgPtr,
                          (OS_MSG_SIZE) OSIntQOutPtr->MsgSize,
                          (OS_OPT     ) OSIntQOutPtr->Opt,
                          (CPU_TS     ) OSIntQOutPtr->TS,
                          (OS_ERR    *)&err);
#endif
             break;                 //跳出

        case OS_OBJ_TYPE_TASK_RESUME://如果对象类型是恢复任务
#if OS_CFG_TASK_SUSPEND_EN > 0u      //如果使能了函数OSTaskResume()，恢复该任务
             (void)OS_TaskResume((OS_TCB *) OSIntQOutPtr->ObjPtr,
                                 (OS_ERR *)&err);
#endif
             break;                  //跳出

        case OS_OBJ_TYPE_TASK_SIGNAL://如果对象类型是任务信号量
             (void)OS_TaskSemPost((OS_TCB *) OSIntQOutPtr->ObjPtr,//发布任务信号量
                                  (OS_OPT  ) OSIntQOutPtr->Opt,
                                  (CPU_TS  ) OSIntQOutPtr->TS,
                                  (OS_ERR *)&err);
             break;                  //跳出

        case OS_OBJ_TYPE_TASK_SUSPEND://如果对象类型是挂起任务
#if OS_CFG_TASK_SUSPEND_EN > 0u       //如果使能了函数 OSTaskSuspend()，挂起该任务
             (void)OS_TaskSuspend((OS_TCB *) OSIntQOutPtr->ObjPtr,
                                  (OS_ERR *)&err);
#endif
             break;                   //跳出

        case OS_OBJ_TYPE_TICK:       //如果对象类型是时钟节拍
#if OS_CFG_SCHED_ROUND_ROBIN_EN > 0u //如果使能了时间片轮转调度，
             OS_SchedRoundRobin(&OSRdyList[OSPrioSaved]); //轮转调度进中断前优先级任务
#endif

             (void)OS_TaskSemPost((OS_TCB *)&OSTickTaskTCB, //发送信号量给时钟节拍任务
                                  (OS_OPT  ) OS_OPT_POST_NONE,
                                  (CPU_TS  ) OSIntQOutPtr->TS,
                                  (OS_ERR *)&err);
#if OS_CFG_TMR_EN > 0u               //如果使能了软件定时器，发送信号量给定时器任务
             OSTmrUpdateCtr--;
             if (OSTmrUpdateCtr == (OS_CTR)0u) {
                 OSTmrUpdateCtr = OSTmrUpdateCnt;
                 ts             = OS_TS_GET();                             
                 (void)OS_TaskSemPost((OS_TCB *)&OSTmrTaskTCB,             
                                      (OS_OPT  ) OS_OPT_POST_NONE,
                                      (CPU_TS  ) ts,
                                      (OS_ERR *)&err);
             }
#endif
             break;                  //跳出

        default:                     //如果内核对象类型超出预期
             break;                  //直接跳出
    }
}
```

该函数的整个流程也是非常简单的，首先提取出中断队列中的一个信息块的信息，根据发布的内核对象类型分类处理，在前面我们已经讲解过了全部内核对象发布（释放）的过程，就直接在任务中调用这些发布函数根据对应的内核对象进行发布。值得注意的是时钟节拍类型 OS_OBJ_TYPE_TICK，如果没有使能中断延迟发布的宏定义，那么所有跟时钟节拍相关的，包括时间片轮转调度，定时器，发送消息给时钟节拍任务等都是在中断中执行，而使用延迟提交就把这些工作都放到延迟发布任务中执行。**延迟发布之所以能够减少关中断的时间是因为在这些内核对象发布函数中，进入临界段都是采用锁调度器的方式，如果没有使用延迟发布，提交的整个过程都要关中断**。 
