#include "espressif/esp_common.h"
#include "esp/uart.h"
#include <string.h>
#include "FreeRTOS.h"
#include "task.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"
#include "ipv4/lwip/ip_addr.h"
#include "ssid_config.h"
//#include "debug_dumps.h"
#include <algorithm>

#define WEB_SERVER "marzipan-Lenovo-ideapad-Y700-15ISK"
#define WEB_PORT 50007
#define pkt_size (28*10)

class HostCommManager {


    public:
        
        int initialize(){
            _initialize();
            return 0;
        }

        int update(){
            int rcode = _process_tcp_command();
            if (rcode < 0){
                _establish_host_connection();
            }
            return rcode;
        }

    private:

        // Variables
        int mSocket = -1;
        char mOutbuf[pkt_size] = {0};
        char mInbuf[pkt_size] = {0};

        // Connect to host
        void _establish_host_connection(){

            //TODO Check if tcp connection is already established, run if not established

            struct addrinfo res;
            struct ip_addr my_host_ip;
            IP4_ADDR(&my_host_ip, 192, 168, 1, 168);

            //struct sockaddr_in my_sockaddr_in = {
            //    .sin_addr.s_addr = my_host_ip.addr,
            //    .sin_len = sizeof(struct sockaddr_in),
            //    .sin_family = AF_INET,
            //    .sin_port = htons(WEB_PORT),
            //    .sin_zero = 0        
            //};

            struct sockaddr_in my_sockaddr_in;
            my_sockaddr_in.sin_addr.s_addr = my_host_ip.addr;
            my_sockaddr_in.sin_len = sizeof(struct sockaddr_in);
            my_sockaddr_in.sin_family = AF_INET;
            my_sockaddr_in.sin_port = htons(WEB_PORT);
            std::fill_n(my_sockaddr_in.sin_zero, 8, (char)0x0);

            res.ai_addr = (struct sockaddr*) (void*)(&my_sockaddr_in);
            res.ai_addrlen = sizeof(struct sockaddr_in);
            res.ai_family = AF_INET;
            res.ai_socktype = SOCK_STREAM;

            struct in_addr *addr = &((struct sockaddr_in *)res.ai_addr)->sin_addr;
            printf("DNS lookup succeeded. IP=%s\r\n", inet_ntoa(*addr));

            while(1) {

                mSocket = socket(res.ai_family, res.ai_socktype, 0);
                if(mSocket < 0) {
                    printf("... Failed to allocate socket.\r\n");
                    //freeaddrinfo(res);
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }

                printf("... allocated socket\r\n");

                if(connect(mSocket, res.ai_addr, res.ai_addrlen) != 0) {
                    close(mSocket);
                    //freeaddrinfo(res);
                    printf("... socket connect failed.\r\n");
                    vTaskDelay(4000 / portTICK_PERIOD_MS);
                    continue;
                }

                printf("... connected\r\n");
                break;
            }
        }

        // Process tcp command
        int _process_tcp_command(){

            if (mSocket < 0){
                return -1;
            }

            int r = read(mSocket, mInbuf, pkt_size);
            if (r > 0){
                printf("received: %s", mInbuf);

                // Switch or else if to all possible byte commands here
                if (mInbuf[0] == 0x1){
                    printf("Received OTA Command");
                    if (write(mSocket, "OTA", 3) < 0){
                        printf("failed to send ACK");
                    }
                    else {
                        printf("ACK sent");
                        return mInbuf[0];
                    }
                }
                return 0;
            }
            else if (r == 0){
                // received nothing, but no error
            }
            else {
                // TODO Handle Error
                return -1;
            }
        }

        void _initialize(void)
        {
            printf("Initializing WiFi config");

            struct sdk_station_config config;
            memcpy(config.ssid, WIFI_SSID, strlen((const char*) WIFI_SSID)+1);
            memcpy(config.password, WIFI_PASS, strlen((const char*) WIFI_PASS)+1);

            /* required to call wifi_set_opmode before station_set_config */
            sdk_wifi_set_opmode(STATION_MODE);
            sdk_wifi_station_set_config(&config);
        }
};
