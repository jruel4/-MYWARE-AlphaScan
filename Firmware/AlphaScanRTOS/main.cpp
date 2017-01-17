#include "task.hpp"
#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "SoftAP.cpp"

class AlphaScanManager : public esp_open_rtos::thread::task_t
{
    public:

        // Variables

        // Methods
        void setDebugSerial(bool set){
            mDebugSerial = set;
        }

        void init(){
            initialize();
        }

    private:

        // Modules
        SoftAP c_SoftAp;        

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
                            //
                            break;
                        }
                    default:
                        {
                            //
                            break;
                        }
                }
            }
        }    

        void initialize(){
            if (mDebugSerial){
                uart_set_baud(0, 74880);
                printf("Initializing Alpha Scan with Debug Mode = true");
            }

            c_SoftAp.initialize();
            mMainLoopCounter = 0;
            mSystemState = AP_MODE;
        }
};

AlphaScanManager t_Manager;

/**
 * 
 */
extern "C" void user_init(void)
{
    t_Manager.setDebugSerial(true);
    t_Manager.init();
    //t_Manager.task_create("main_loop");
}
