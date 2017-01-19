#include "task.hpp"
#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "Modules/SoftApManager.cpp"
#include "Modules/OtaManager.cpp"
#include "Modules/HostCommManager.cpp"
#include "Modules/ads_ctrl.cpp"

#define FIRMARE_VERSION "0.0.4"

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
        ADS c_Ads;
        
        // Variables
        bool mDebugSerial;
        uint32_t mMainLoopCounter;        
        enum T_SYSTEM_STATE {
            AP_MODE,
            RUN_MODE
        } mSystemState;

        // Methods
        void task()
        {
            _initialize();
            if (mDebugSerial){
                printf("AlphaScanManager:task(): start\n");
            }
            while(true) {
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
                            if (mDebugSerial && (mMainLoopCounter++ % (int)10E7 == 0)) {
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
            }
            else if (rcode == 0x02){
                printf("running ads code\n");
                // Print Reg Map Serial
                c_Ads.setupADS();
                c_Ads.printSerialRegistersFromADS();
                printf("completed ads code\n");
            }
            else if (rcode == 0x03){
                printf("running test signal stream code\n");

                //TODO Setup ADS
                
                // Receive new data from ADS - send to host
                // Check TCP read for terminate command
                c_HostComm.stream_ads(&c_Ads);

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
    t_Manager.setDebugSerial(true);
    t_Manager.task_create("main_loop");
}
