#include "task.hpp"
#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "Modules/SoftApManager.cpp"
#include "Modules/OtaManager.cpp"
#include "Modules/HostCommManager.cpp"

#define FIRMARE_VERSION "0.0.1"

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
                            if (mDebugSerial && (mMainLoopCounter++ % 1000 == 0)) {
                                printf("mSystemState == AP_MODE");
                            }
                            break;
                        }
                    case RUN_MODE:
                        {
                            if (mDebugSerial && (mMainLoopCounter++ % 1000 == 0)) {
                                printf("mSystemState == RUN_MODE");
                            }

                            int rcode = c_HostComm.update();
                            if (rcode > 0){
                                if (mDebugSerial){
                                    printf("Triggering task: %d",rcode);
                                }
                                // Trigger corresponding task
                                _trigger_task(rcode);
                            }

                            break;
                        }
                    default:
                        {
                            if (mDebugSerial && (mMainLoopCounter++ % 1000 == 0)) {
                                printf("mSystemState == Invalid State");
                            }
                            break;
                        }
                }
            }
        }    

        void _initialize(){
            if (mDebugSerial){
                uart_set_baud(0, 74880);
                printf("Initializing Alpha Scan with Debug Mode = true");
                printf("Fimare Version %s", FIRMARE_VERSION);
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
