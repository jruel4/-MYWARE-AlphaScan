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
        int mKeepAliveCounter = 0;

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
                printf("mSocket = %d\n",mSocket);

                if(mSocket < 0) {
                    printf("... Failed to allocate socket.\r\n");
                    //freeaddrinfo(res);
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }

                printf("... allocated socket\r\n");

                nbset = 0;
                ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
                printf("set blocking: %d\n", ctlr);

                if(connect(mSocket, res.ai_addr, res.ai_addrlen) != 0) {
                    printf("Closing socket: %d\n",mSocket);
                    close(mSocket);
                    //freeaddrinfo(res);
                    printf("... socket connect failed.\r\n");
                    vTaskDelay(4000 / portTICK_PERIOD_MS);
                    continue;
                }

                nbset = 1;
                ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
                printf("set non blocking: %d\n", ctlr);

                //int optval = 1;
                //setsockopt(mSocket, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval));
                //printf("set keep alive tcp option");

                printf("... connected\r\n");
                break;
            }
        }

        // Process tcp command
        int _process_tcp_command(){

            int rready = _read_ready(true);
            if (rready < 0){
                printf("closing socket: %d",mSocket);
                close(mSocket);
                return rready;
            }
            else if ( rready == 0){
                return rready;
            }
            else {
                //proceed with read
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
                        printf("Closing socket: %d\n",mSocket);
                        close(mSocket);
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
                printf("_tcp_handle_command r=%d\n",r);
                printf("Closing socket: %d\n",mSocket);
                close(mSocket);
                //printf("rsel = %d\n",rsel);
                //printf("mSocket=%d\n", mSocket);
                //for (int i = 0 ; i < sizeof((long int)fds.fds_bits); i++){
                //    printf("fd_bits[%d] = %d\n", i, fds.fds_bits[i]);
                //}
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
            
            bool FAKE_MODE = false;

            printf("Initializing internal ADS stream call\n");
            int r;
            int write_result;
            // setup ads streaming, interrupt, etc.
            ads->configureTestSignal();
            ads->startStreaming();
            // Generate fake square wave buffer
            uint16_t tCounter = 0;
            bool tBool = false;

            char outbuf_high[24] = {0};
            for (int i  = 0; i < 8; i++){
                outbuf_high[i*3] = 0x1;
            }

            char outbuf_low[24] = {0};
            unsigned char inbuf[29] = {0};
            //unsigned char inbufBig[256] = {0};

            int c = 0;
            long total_tx = 0;
            uint8_t block_counter = 0;
            uint32_t dReadyCounter = 0;
            int nbset, ctlr;
            while (1){

                // Set non blocking
                nbset = 1;
                ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
                //printf("set non blocking: %d\n", ctlr);

                int rready = _read_ready(false);
                if (rready < 0){
                    printf("Connection died\n");
                    printf("Closing socket: %d\n",mSocket);
                    close(mSocket);
                    break;
                }
                else if (rready == 0){
                    // no new commands
                    //continue;
                }
                else{
                    // proceed with read operation


                    // Read TCP in for stop op code
                    int r = read(mSocket, mInbuf, pkt_size);
                    //r = lwip_recv(mSocket, mInbuf, pkt_size, 0);
                    //r = lwip_recv(mSocket, mInbuf, pkt_size, MSG_DONTWAIT);
                    printf("return from lwip_recv with r=%d\n",r);
                    if (r > 0){
                        printf("received: %s", mInbuf);
                        if (mInbuf[0] == 0xf){
                            // terminate stream
                            printf("received terminate command\n");
                            break;
                        }
                    }
                    else if (r < 0){
                        printf("r < 0");
                        // Check if connection is alive
                        if (write(mSocket, "ACK", 3) < 0){
                            printf("failed to receive ACK");
                            printf("Closing socket: %d\n",mSocket);
                            close(mSocket);
                            break;
                        }
                    }
                }

                nbset = 0;
                ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
                //printf("set blocking: %d\n", ctlr);


                // if new data is ready, send it over wifi to host

                // Add fake square wave code here

                //add delay
                if (FAKE_MODE){
                    vTaskDelay( 30 / portTICK_PERIOD_MS); // should send at 100 Hz

                    if (tCounter++ % 200 == 0){
                        printf("toggling: %d\n", tBool);
                        tBool = !tBool;    
                    }

                    if (tBool){
                        write_result = write(mSocket, outbuf_high, 24); 
                    }
                    else {
                        write_result = write(mSocket, outbuf_low, 24); 
                    }

                    if (write_result < 0){
                        printf("failed to write outbuf, no ack");
                        printf("Closing socket: %d\n",mSocket);
                        close(mSocket);
                        break;
                    }
                    else {
                        //printf("Sent outbuf");
                    }
                }

                else{


                    // Get sample from ADS
                    //vTaskDelay( 5 / portTICK_PERIOD_MS); // should send at 100 Hz
                    //taskYIELD();

                    if (tCounter++ % 2000 == 0){
                        //printf("toggling: %d\n", tBool);
                        tBool = !tBool;    
                    }

                    //if (ads->getDataFake(inbuf, tBool))
                    //if (ads->getData(inbuf, 0)) //Nonblocking b/c of 0
                    int inWaiting;
                    TickType_t tickTimestamp;
                    while ((inWaiting = ads->getDataWaiting(inbuf, 0, tickTimestamp)), inWaiting > 0) //Nonblocking b/c of 0
                    {
                        //{
                        //    for (int j = 0; j < 8; j++){
                        //        long valueCH8 = 0;
                        //        for(int i = 0; i < 3; ++i) valueCH8 += (inbuf[3*j+i+3] << (2-i)*8);
                        //        //printf(" %d", valueCH8);
                        //    }
                        //    //printf("\n");
                        //}
                        inbuf[0] = 0x7f;
                        inbuf[1] = 0x7f;
                        inbuf[2] = 0x7f;
                        inbuf[3] = 0x7f;
                        inbuf[4] = block_counter++;

                        //inbuf[5] = (dReadyCounter >> 16) & 0xff;
                        //inbuf[6] = (dReadyCounter >> 8) & 0xff;
                        inbuf[5] = 0;
                        inbuf[6] = 0;
                        inbuf[7] = (inWaiting >> 0) & 0xff;

                        inbuf[8] = (tickTimestamp >> 16) & 0xff;
                        inbuf[9] = (tickTimestamp >> 8) & 0xff;
                        inbuf[10] = (tickTimestamp >> 0) & 0xff;


                        dReadyCounter = 0;

                        //set both timval struct to zero
                        //struct timeval tv;
                        //tv.tv_sec = 0;
                        //tv.tv_usec = 0;
                        //fd_set fds;
                        //FD_ZERO(&fds);
                        //FD_SET(mSocket, &fds);

                        //while (select( mSocket + 1, NULL , &fds, NULL, &tv ) < 1) {
                        //    tv.tv_sec = 0;
                        //    tv.tv_usec = 0;
                        //    FD_ZERO(&fds);
                        //    FD_SET(mSocket, &fds);
                        //    c++;
                        //}

                        //vTaskDelay( 1 / portTICK_PERIOD_MS); // should send at 100 Hz
                        write_result = write(mSocket, inbuf, 29); 
                        if (write_result != 29){
                            printf("write_result: %d\n",write_result);
                        }
                        total_tx += write_result;
                        c++;

                        //printf("select af: %d \n\n", select( mSocket + 1, NULL , &fds, NULL, &tv ));
                        //while( select( mSocket + 1, NULL , &fds, NULL, &tv ) > 0){
                        //    c++;
                        //    vTaskDelay( 1 / portTICK_PERIOD_MS); // should send at 100 Hz
                        //}
                        //printf("Delayed for %d loops",c);


                        if (write_result < 0){
                            printf("total_tx: %d\n",total_tx);
                            printf("failed 1x to rx ACK");
                            vTaskDelay( 1 / portTICK_PERIOD_MS); // should send at 100 Hz
                            write_result = write(mSocket, inbuf, 29); 
                            if (write_result < 0){
                                printf("failed to write outbuf, no ack");
                                printf("Closing socket: %d\n",mSocket);
                                close(mSocket);
                                return;
                            }
                        }
                        else {
                            //for (int j = 0; j < 8; j++){
                            //    long valueCH8 = 0;
                            //    for(int i = 0; i < 3; ++i) valueCH8 += (inbuf[3*j+i+3] << (2-i)*8);
                            //    printf(" %f", valueCH8);
                            //}
                            //printf("\n");
                        }
                    }
                }
            }
        }

        int _read_ready(bool check_alive){

            // Periodically check connection
            if (check_alive && (mKeepAliveCounter++ > 10E3)){
                mKeepAliveCounter = 0;
                if (write(mSocket, "ACK", 3) < 0){
                    printf("failed to receive ACK");
                    return -1;
                }
            }

            if (mSocket < 0){
                printf("mSocket < 0 - ERR\n");
                return -1;
            }

            fd_set fds;
            FD_ZERO(&fds);
            FD_SET(mSocket, &fds);

            //set both timval struct to zero
            struct timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 0;

            int rsel = select( mSocket + 1, &fds , NULL, NULL, &tv );
            if (rsel < 1) {
                return 0;
            }
            else {
                // this is the only situation (i.e. socket is valid and ready to read) that should allow calling read()
                return 1;
            }
        }
};
