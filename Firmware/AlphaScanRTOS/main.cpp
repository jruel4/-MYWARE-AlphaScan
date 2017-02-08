#define LWIP_DEBUG
#include "task.hpp"
#include "esp/timer.h"
#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "esp/spi.h"
#include "lwip/stats.h"
#include "Modules/SoftApManager.cpp"
#include "Modules/OtaManager.cpp"
#include "Modules/HostCommManager.cpp"
#include "Modules/ads_ctrl.cpp"

#define FIRMARE_VERSION "0.0.15"

class AlphaScanManager : public esp_open_rtos::thread::task_t
{
    public:

        // Variables

        // Methods
        void setDebugSerial(bool set){
            mDebugSerial = set;
        }

    private:

        // Main Control Classes
        SoftAP c_SoftAp;        
        HostCommManager c_HostComm;
        OtaManager c_Ota; 
        ADS* c_Ads = new ADS(SPI_FREQ_DIV_10M);
        
        // Variables
        bool mDebugSerial;
        uint32_t mMainLoopCounter;        
        enum T_SYSTEM_STATE {
            AP_MODE,
            RUN_MODE,
            OTA_MODE
        } mSystemState;

        // Methods
        void task()
        {
            _initialize();
            if (mDebugSerial){
                printf("AlphaScanManager:task(): start\n");
            }
            while(1) {
                switch (mSystemState){
                    case AP_MODE:
                        {
                            //
                            if (mDebugSerial && (mMainLoopCounter++ % 10000 == 0)) {
                                printf("mSystemState == AP_MODE\n");
                            }
                            break;
                        }
                    case RUN_MODE:
                        {
                            if (mDebugSerial && (mMainLoopCounter++ % (int)10E5 == 0)) {
                                printf("mSystemState == RUN_MODE\n");
                            }

                            int rcode = c_HostComm.update();
                            if (rcode > 0){
                                if (mDebugSerial){
                                    printf("Triggering task: %d\n",rcode);
                                }
                                // Trigger corresponding task
                                _trigger_task(rcode);
                            }

                            break;
                        }
                    case OTA_MODE:
                        {
                            //do nothing
                            break;
                        }
                    default:
                        {
                            if (mDebugSerial && (mMainLoopCounter++ % 1000 == 0)) {
                                printf("mSystemState == Invalid State\n");
                            }
                            break;
                        }
                }
            }
        }    

        void _initialize(){
            if (mDebugSerial){
                uart_set_baud(0, 74880);
                printf("Initializing Alpha Scan with Debug Mode = true\n");
                printf("Fimare Version %s\n", FIRMARE_VERSION);
            }

            //c_SoftAp.initialize();
            c_HostComm.initialize();
            mMainLoopCounter = 0;
            mSystemState = RUN_MODE;
        }

        void _trigger_task(int rcode){
            if (rcode == 0x01){ 
                // OTA Mode 
                c_Ota.run();
                mSystemState = OTA_MODE;
                printf("Exited from OTA\n");
            }
            else if (rcode == 0x02){
                printf("running ads code\n");
                // Print Reg Map Serial
                c_Ads->printSerialRegistersFromADS();
                printf("completed ads code\n");
            }
            else if (rcode == 0x03){
                printf("running test signal stream code\n");

                // Receive new data from ADS - send to host
                c_HostComm.stream_ads(c_Ads);

                printf("test signal stream completed\n");
            }
            // ... complete command responses
        }
};

AlphaScanManager t_Manager;

/**
 * 
 */
extern "C" void user_init(void)
{
    vTaskDelay(15 / portTICK_PERIOD_MS);
    t_Manager.setDebugSerial(true);

    t_Manager.task_create("main_loop", 2048);//TODO increase task stack depth to avoid overflow
}

/**
  setting up timer for debug dumps
 **/
//#define ETS_UNCACHED_ADDR(addr) (addr)
//#define ETS_CACHED_ADDR(addr) (addr)
//#define PERIPHS_TIMER_BASEDDR 0x60000600
//#define READ_PERI_REG(addr) (*((volatile uint32_t *)ETS_UNCACHED_ADDR(addr)))
//#define WRITE_PERI_REG(addr, val) (*((volatile uint32_t *)ETS_UNCACHED_ADDR(addr))) = (uint32_t)(val)
//#define RTC_REG_READ(addr)                        READ_PERI_REG(PERIPHS_TIMER_BASEDDR + addr)
//#define RTC_REG_WRITE(addr, val) WRITE_PERI_REG(PERIPHS_TIMER_BASEDDR + addr, val)
////load initial_value to timer1
//#define FRC1_LOAD_ADDRESS                    0x00
////timer1's counter value(count from initial_value to 0)
//#define FRC1_COUNT_ADDRESS                 0x04
//#define FRC1_CTRL_ADDRESS                    0x08
////clear timer1's interrupt when write this address
//#define FRC1_INT_ADDRESS                      0x0c
//#define FRC1_INT_CLR_MASK 0x00000001
//#define FRC1_ENABLE_TIMER BIT7

//typedef enum {
//    DIVDED_BY_1 = 0,
//    DIVDED_BY_16 = 4,
//    DIVDED_BY_256 = 8,
//} TIMER_PREDIVED_MODE;

extern "C" void vConfigureTimerForRunTimeStats( void ) {
    //    RTC_REG_WRITE(FRC1_CTRL_ADDRESS,  //FRC2_AUTO_RELOAD|
    //            DIVDED_BY_256
    //            | FRC1_ENABLE_TIMER);
    //
    //    RTC_REG_WRITE(FRC1_LOAD_ADDRESS, 0);
    timer_set_interrupts(FRC2, false);
    timer_set_run(FRC2, false);
    timer_set_frequency(FRC2, 1000);
    //timer_set_load(FRC2, 0x7fffff);
    timer_set_run(FRC2, true);
}

extern "C" uint32_t vGetRunTimerCountValue( void ){
    return timer_get_count(FRC2);
}

//extern void vConfigureTimerForRunTimeStats( void );
//#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() vConfigureTimerForRunTimeStats()
//#define portGET_RUN_TIME_COUNTER_VALUE() RTC_REG_READ(FRC1_COUNT_ADDRESS)
