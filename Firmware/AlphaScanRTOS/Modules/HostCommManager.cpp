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
#include <algorithm>
#include "ads_ctrl.cpp"

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

        void stream_ads(ADS* ads){
            _stream_ads(ads);
        }

    private:

        // Variables
        int mSocket = -1;
        char mOutbuf[pkt_size] = {0};
        char mInbuf[pkt_size] = {0};

        // Connect to host
        void _establish_host_connection(){

            struct addrinfo res;
            struct ip_addr my_host_ip;
            IP4_ADDR(&my_host_ip, 192, 168, 1, 168);

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

            int nbset = 1;
            int ctlr = -2;
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

                ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
                printf("set non blocking: %d\n", ctlr);

                printf("... connected\r\n");
                break;
            }
        }

        // Process tcp command
        int _process_tcp_command(){

            if (mSocket < 0){
                printf("mSocket < 0 - ERR\n");
                return -1;
            }

            fd_set fds;
            FD_SET(mSocket, &fds);
            
            //set both timval struct to zero
            struct timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 0;

            if (select( mSocket + 1, &fds , NULL, NULL, &tv ) < 1) {
                return 0;
            }
            
            int r = read(mSocket, mInbuf, pkt_size);
            if (r > 0){
                printf("received: %s", mInbuf);

                //////////////////////////////////////////////////////////
                // OTA
                //////////////////////////////////////////////////////////
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
                //////////////////////////////////////////////////////////
                // Dump ADS Register to Serial
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x2){
                    // print reg map
                    printf("Received reg map dump command");
                    return mInbuf[0];
                }
                //////////////////////////////////////////////////////////
                // Begin Test Signal Streaming
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x3){
                    printf("Received ADS Test Signal Stream command \n");
                    return mInbuf[0];

                }
                //////////////////////////////////////////////////////////
                // 
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x4){

                }
                //////////////////////////////////////////////////////////
                // 
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x5){

                }
                //////////////////////////////////////////////////////////
                // 
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x6){

                }
                //////////////////////////////////////////////////////////
                // 
                //////////////////////////////////////////////////////////
                else if (mInbuf[0] == 0x7){

                }
                return 0;
            }
            else if (r==0){
                return 0;
            }
            else {
                // TODO Handle Error
                printf("r=%d\n",r);
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

        void _stream_ads(ADS* ads){

            printf("Initializing internal ADS stream call\n");
            int r;

            while (1){

                // Read TCP in for stop op code
                int r = read(mSocket, mInbuf, pkt_size);
                //r = lwip_recv(mSocket, mInbuf, pkt_size, 0);
                //r = lwip_recv(mSocket, mInbuf, pkt_size, MSG_DONTWAIT);
                printf("return from lwip_recv with r=%d\n",r);
                if (r > 0){
                    printf("received: %s", mInbuf);
                    if (mInbuf[0] == 0xff){
                        // terminate stream
                        printf("received terminate command\n");
                        break;
                    }
                }

                //TODO Perform ADS update and shipp output back to host
                
            }
        }
};
