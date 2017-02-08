#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "esp/timer.h"
#include <string.h>
#include "FreeRTOS.h"
#include "task.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
//#include "../../../../AlphaScanRTOS/lwip/lwip/src/api/sockets.c"
#include "lwip/sys.h"
#include "lwip/tcp.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"
#include "lwip/memp.h"
#include "lwip/stats.h"
#include "ipv4/lwip/ip_addr.h"
#include "ssid_config.h"
#include <algorithm>
#include "ads_ctrl.cpp"
#include "lwip/api.h"
//JCR
//extern struct lwip_sock;
//extern struct netconn;

//extern struct lwip_sock {
  /** sockets currently are built on netconns, each socket has one netconn */
  //struct netconn *conn;
  /** data that was left from the previous read */
  //void *lastdata;
  /** offset in the data that was left from the previous read */
  //u16_t lastoffset;
  /** number of times data was received, set by event_callback(),
      tested by the receive and select functions */
  //s16_t rcvevent;
  /** number of times data was ACKed (free send buffer), set by event_callback(),
      tested by select */
  //u16_t sendevent;
  /** error happened for this socket, set by event_callback(), tested by select */
  //u16_t errevent; 
  /** last error that occurred on this socket */
  //int err;
  /** counter of how many threads are waiting for this socket using select */
  //int select_waiting;
//};


//extern static struct lwip_sock * get_socket(int s);
//extern err_t tcp_output(struct tcp_pcb *pcb);


#define WEB_SERVER "marzipan-Lenovo-ideapad-Y700-15ISK"
#define WEB_PORT 50007
#define SAMPLE_SIZE (29)
#define SAMPLES_PER_PACKET (4*7)
#define PACKET_SIZE (SAMPLE_SIZE * SAMPLES_PER_PACKET)

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
			//_stream_ads(ads);
            _stream_task(ads);
		}

	private:

		// Variables
		int mSocket = -1;
		unsigned char mOutbuf[PACKET_SIZE] = {0};
		unsigned char mInbuf[PACKET_SIZE] = {0};
		int mKeepAliveCounter = 0;
		const static int TEST_BUF_LEN = 256;
		char test_outbuf[TEST_BUF_LEN] = {0};
        static const int pkt_size = 1400;
        static const int inbuf_size = 3;

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
			int optval = 1;
            // Only attempt for 10 seconds, otherwise restart...
            int retry_max = (int)(30.0/0.300);
            int retry_ctr = 0;

            printf("Attempting to establish host connection\n");
			while(1) {

                if (retry_ctr++ > retry_max){
                    retry_ctr = 0;
                    printf("Resetting device (host connect timed out\n");
                    printf("heap size: %d\n", xPortGetFreeHeapSize());
                    //sdk_system_restart();
                }

				//get_pool_sizes();
				//printf("heap size: %d\n", xPortGetFreeHeapSize());

				mSocket = socket(res.ai_family, res.ai_socktype, 0);
				//TODO maybe put this back in: lwip_setsockopt(mSocket, IPPROTO_TCP, TCP_NODELAY, (void*)&optval, sizeof(optval));

				//printf("mSocket = %d\n",mSocket);

				if(mSocket < 0) {
					//printf("... Failed to allocate socket.\r\n");
					//freeaddrinfo(res);
					vTaskDelay(400 / portTICK_PERIOD_MS);
					continue;
				}

				//printf("... allocated socket\r\n");

				nbset = 0;
				ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);

				if(connect(mSocket, res.ai_addr, res.ai_addrlen) != 0) {
					//printf("Closing socket: %d\n",mSocket);
					close(mSocket);
					//freeaddrinfo(res);
					//printf("... socket connect failed.\r\n");
					vTaskDelay(400 / portTICK_PERIOD_MS);
					continue;
				}

				nbset = 1;
				ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);

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

			int r = read(mSocket, mInbuf, PACKET_SIZE);
			if (r > 0){
				printf("received: %s", mInbuf);

				//////////////////////////////////////////////////////////
				// OTA
				//////////////////////////////////////////////////////////
				if (mInbuf[0] == 0x1){
					printf("Received OTA Command");
					if (write(mSocket, "OTA", 3) < 0){
						printf("closing socket: %d\n",mSocket);
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
				// Restart Device
				//////////////////////////////////////////////////////////
				else if (mInbuf[0] == 0x4){
                    sdk_system_restart();
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
				printf("closing socket: %d\n",mSocket);
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

		int _read_ready(bool check_alive){

			// Periodically check connection
			if (check_alive && (mKeepAliveCounter++ > 5E3)){
				mKeepAliveCounter = 0;
                int retry_counter = 0;
                int result = -1;
                while (result = write(mSocket, "ACK", 3), result < 0){
                    vTaskDelay(10 / portTICK_PERIOD_MS);
                    if (++retry_counter > 3)
                    {
                        return -1;
                    }
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


        void _stream_task(ADS* ads) {

            // Setup remote address
            struct ip_addr my_host_ip;
            IP4_ADDR(&my_host_ip, 192, 168, 1, 168);

            struct sockaddr_in my_sockaddr_in;
            my_sockaddr_in.sin_addr.s_addr = my_host_ip.addr;
            my_sockaddr_in.sin_len = sizeof(struct sockaddr_in);
            my_sockaddr_in.sin_family = AF_INET;
            my_sockaddr_in.sin_port = htons(WEB_PORT);
            std::fill_n(my_sockaddr_in.sin_zero, 8, (char)0x0);

            struct addrinfo res;
            res.ai_addr = (struct sockaddr*) (void*)(&my_sockaddr_in);
            res.ai_addrlen = sizeof(struct sockaddr_in);
            res.ai_family = AF_INET;
            res.ai_socktype = SOCK_DGRAM;

            // Setup local address
            struct sockaddr_in my_sock_addr_x;
            my_sock_addr_x.sin_addr.s_addr = htonl(INADDR_ANY);
            my_sock_addr_x.sin_len = sizeof(struct sockaddr_in);
            my_sock_addr_x.sin_family = AF_INET;
            my_sock_addr_x.sin_port = htons(WEB_PORT);
            std::fill_n(my_sock_addr_x.sin_zero, 8, (char)0x0);

            struct addrinfo res_x;
            res_x.ai_addr = (struct sockaddr*) (void*)(&my_sock_addr_x);
            res_x.ai_addrlen = sizeof(struct sockaddr_in);
            res_x.ai_family = AF_INET;
            res_x.ai_socktype = SOCK_DGRAM;

            while(1) {

                // Allocated socket
                int s = socket(res_x.ai_family, res_x.ai_socktype, 0);
                if(s < 0) {
                    printf("... Failed to allocate UDP socket.\r\n");
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }
                printf("... allocated UDP socket\r\n");

                // Bind local socket
                if(bind(s, res_x.ai_addr, res_x.ai_addrlen) < 0) {
                    close(s);
                    printf("bind failed.\r\n");
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }
                printf("... UDP bind success\r\n");

                // Init stream variables
                byte outbuf[pkt_size] = {0};
                byte inbuf[inbuf_size] = {0};
                uint8_t pkt_cnt = 0;
                uint8_t drop_count = 0;
                bool local_buf_acked = true;
                int inWaiting = 0;
                int heapSize = 0;


                printf("Seting up ADS\n");
                ads->configureTestSignal();
                printf("Begin streaming\n");
                ads->startStreaming();

                /******************************** 
                  Main stream loop
                 *********************************/

                while(1) {

                    // If new data in local buf, send it
                    if (!local_buf_acked) {
                        if (sendto(s, outbuf, pkt_size, 0, res.ai_addr, res.ai_addrlen ) < 0) {
                            printf("... socket send failed\r\n");
                            close(s);
                            break;
                        }
                    }

                    // If local buf is free, check queue for new packet's worth of data
                    if (local_buf_acked){
                        inWaiting = ads->getQueueSize();
                        if (inWaiting >= 57){
                            // Fill local buffer with new data
                            if (ads->getDataPacket(outbuf)){ 
                                local_buf_acked = false;
                            }
                            else{
                                printf("Failed to load outbuf, file: %s, line: %d\n",__FILE__,__LINE__);
                            }
                        }
                    }

                    // Blocking read for ACK on currently buffered packet
                    recvfrom(s, inbuf, inbuf_size, 0, res.ai_addr, &(res.ai_addrlen)); 
                    if (inbuf[0] == outbuf[0])
                    {
                        // It's a proper ACK, move to next packet
                        outbuf[0] = ++pkt_cnt;
                        local_buf_acked = true;

                        // Get status data
                        outbuf[1] = (inWaiting >> 8) & 0xff;
                        outbuf[2] = inWaiting & 0xff;
                        heapSize = xPortGetFreeHeapSize();
                        outbuf[3] = (heapSize >> 16) & 0xff;
                        outbuf[4] = (heapSize >> 8)  & 0xff;
                        outbuf[5] = (heapSize >> 0)  & 0xff;
                    }
                    else  {
                        if (inbuf[2] == 0xff){
                            ads->stopStreaming();
                            close(s);
                            printf("Received TERMINATE command\n");
                            return;
                        }
                        drop_count++;
                    }
                }
            }
        }
};
