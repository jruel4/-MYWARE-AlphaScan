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
			_stream_ads(ads);
		}

	private:

		// Variables
		int mSocket = -1;
		unsigned char mOutbuf[PACKET_SIZE] = {0};
		unsigned char mInbuf[PACKET_SIZE] = {0};
		int mKeepAliveCounter = 0;
		const static int TEST_BUF_LEN = 256;
		char test_outbuf[TEST_BUF_LEN] = {0};

		// Connect to host
		void _establish_host_connection(){

			struct addrinfo res;
			struct ip_addr my_host_ip;
			IP4_ADDR(&my_host_ip, 192, 168, 1, 202);

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
			while(1) {

				get_pool_sizes();
				printf("heap size: %d\n", xPortGetFreeHeapSize());

				mSocket = socket(res.ai_family, res.ai_socktype, 0);
				lwip_setsockopt(mSocket, IPPROTO_TCP, TCP_NODELAY, (void*)&optval, sizeof(optval));

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

				//stats_display();
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

			int pkt_full_ctr = 0;
			int pkt_part_ctr = 0;
			int pkt_partial_write_ctr_1 = 0;
			int pkt_partial_write_ctr_2 = 0;
			int pkt_partial_write_ctr_3 = 0;

			printf("\nStarting _stream_ads\n");

			//printf("set blocking: %d\n", ctlr);
			bool FAKE_MODE = false;

			printf("Initializing internal ADS stream call\n");
			int r;
			int write_result;
			// setup ads streaming, interrupt, etc.
			printf("\nStarting _stream_ads 0 \n");
			ads->configureTestSignal();
			printf("\nStarting _stream_ads 1 \n");
			ads->startStreaming();
			printf("\nStarting _stream_ads 2\n");
			// Generate fake square wave buffer
			uint16_t tCounter = 1;
			bool tBool = false;

			char outbuf_high[24] = {0};
			for (int i  = 0; i < 8; i++){
				outbuf_high[i*3] = 0x1;
			}

			char outbuf_low[24] = {0};
			unsigned char inbuf[SAMPLE_SIZE] = {0};
			unsigned char inbufBig[PACKET_SIZE + SAMPLE_SIZE] = {0};
			unsigned int sampleCounter = 0;
			unsigned int bytesExtraOffset = 0; //Keeps track of the additional bytes from an incomplete write


			int c = 0;
			long total_tx = 0;
			uint8_t block_counter = 0;
			uint32_t dReadyCounter = 0;
			int nbset, ctlr;


			//JCR 02-04
			//lwip_sock *socks = get_socket(mSocket);

			//TODO
			//nbset = 0;
			//ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
			while (1){

				int aTest = 0;
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
					printf("\naTest = %d", aTest);
					int r = read(mSocket, mInbuf, PACKET_SIZE);
					//r = lwip_recv(mSocket, mInbuf, PACKET_SIZE, 0);
					//r = lwip_recv(mSocket, mInbuf, PACKET_SIZE, MSG_DONTWAIT);
					printf("return from lwip_recv with r=%d\n",r);
					if (r > 0){
						printf("received: %s", mInbuf);
						if (mInbuf[0] == 0xf){
							// terminate stream
							printf("received terminate command\n");
							printf("\npart_ctr: %d, full_ctr: %d\n",pkt_part_ctr, pkt_full_ctr);
							printf("\npart_write_1: %d, part_write_2: %d, part_write_3: %d\n",pkt_partial_write_ctr_1, pkt_partial_write_ctr_2, pkt_partial_write_ctr_3);
							char wbuf[400] = {0};
							vTaskList(wbuf);
							printf(wbuf);
							printf("--------------\n");
							vTaskGetRunTimeStats(wbuf);
							printf(wbuf);


									printf("heap size: %d\n", xPortGetFreeHeapSize());
stats_display();
							printf("timer_get_count: %d\n",timer_get_count(FRC2));
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

				//nbset = 0;
				//ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
				//printf("set blocking: %d\n", ctlr);


				// if new data is ready, send it over wifi to host

				// Add fake square wave code here

				//add delay
				{

					// Get sample from ADS
					//vTaskDelay( 5 / portTICK_PERIOD_MS); // should send at 100 Hz
					//taskYIELD();


					//if (ads->getDataFake(inbuf, tBool))
					//if (ads->getData(inbuf, 0)) //Nonblocking b/c of 0
					int inWaiting;
					uint32_t loopTimeStamp = 0;
					TickType_t tickTimestamp;
					while ((inWaiting = ads->getDataWaiting(inbuf, 0, tickTimestamp)), inWaiting > 0) //Nonblocking b/c of 0
					{
						//if (tCounter++ % 1000 == 0){
						//stats_display();
						//    //printf("toggling: %d\n", tBool);
						//    tBool = !tBool;    
						//}
						sampleCounter++;
						if(sampleCounter > SAMPLES_PER_PACKET) sampleCounter = 1;
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

						loopTimeStamp = timer_get_count(FRC2);
						inbuf[11] = (loopTimeStamp >> 16) & 0xff;
						inbuf[12] = (loopTimeStamp >> 8) & 0xff;
						inbuf[13] = (loopTimeStamp >> 0) & 0xff;


						memcpy((inbufBig + (SAMPLE_SIZE * (sampleCounter-1)) + bytesExtraOffset), inbuf, SAMPLE_SIZE);

						dReadyCounter = 0;

						//set both timval struct to zero
						struct timeval tv;
						tv.tv_sec = 0;
						tv.tv_usec = 0;
						fd_set fds;
						FD_ZERO(&fds);
						FD_SET(mSocket, &fds);

						//while (select( mSocket + 1, NULL , &fds, NULL, &tv ) < 1) {
						//    tv.tv_sec = 0;
						//    tv.tv_usec = 0;
						//    FD_ZERO(&fds);
						//    FD_SET(mSocket, &fds);
						//    c++;
						//}

						//vTaskDelay( 1 / portTICK_PERIOD_MS); // should send at 100 Hz

						//static int oncey = 0;
						//Here, our buffer has completely filled up; we *need* to send data - if not possible, quit once queue is full
						if (sampleCounter == SAMPLES_PER_PACKET) {
							pkt_full_ctr += 1;
							//if(oncey == 0) printf("Outputing\n");
							//err_t tOutErr = tcp_output(socks->conn->pcb.tcp);
							//if(oncey == 0) { printf("Outputed\n"); oncey=1; }
							write_result = write(mSocket, inbufBig, PACKET_SIZE+bytesExtraOffset); 
							//if (write_result != PACKET_SIZE)
							//{
							//    printf("write_result: %d\n",write_result);
							//}


							//Issue with writing; keep trying to send
							if (write_result < 0){
								//TODO perform more robust cheking before exiting loop
								//printf("failed 1x to rx ACK");
								//printf("heap size before: %d\n", xPortGetFreeHeapSize());
								//printf("Queue Size: %d\n",ads->getQueueSize());
								//NOTE: SAMPLE_QUEUE_SIZE is defined in ads_ctrl.cpp


								//Make blocking
								nbset = 0;
								ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);

								taskYIELD();
								while (ads->getQueueSize() < SAMPLE_QUEUE_SIZE && write_result < 0){
									write_result = write(mSocket, inbufBig, PACKET_SIZE + bytesExtraOffset); 
								}

								//TODO - Account for partial writes; memmov etc...
								if (write_result != (PACKET_SIZE+bytesExtraOffset))
								{
									pkt_partial_write_ctr_1 += 1;

									memmove(inbufBig, (inbufBig + write_result), ((PACKET_SIZE+bytesExtraOffset) - write_result));
									sampleCounter = sampleCounter - ((write_result + SAMPLE_SIZE-1) / SAMPLE_SIZE);
									bytesExtraOffset = write_result % SAMPLE_SIZE;
								}

								//printf("Queue Size: %d\n",ads->getQueueSize());
								//printf("heap size after: %d\n", xPortGetFreeHeapSize());

								//stats_display();

								if (write_result < 0){
									stats_display();
									printf("failed to write outbuf, no ack, Queue size: %d\n",ads->getQueueSize());
									printf("Closing socket: %d\n",mSocket);
									ads->stopStreaming();
									printf("heap size: %d\n", xPortGetFreeHeapSize());
									close(mSocket);
									return;
								}
								else {
									//Set back to non-blocking
									nbset = 1;
									ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
									continue;
								}
								bytesExtraOffset = 0;
							}
							else if (write_result < (PACKET_SIZE + bytesExtraOffset)) {
								//TODO Need to account for partial packet sent; memmov etc...
								pkt_partial_write_ctr_2 += 1;

								memmove(inbufBig, (inbufBig + write_result), ((PACKET_SIZE+bytesExtraOffset) - write_result));
								sampleCounter = sampleCounter - ((write_result + SAMPLE_SIZE -1) / SAMPLE_SIZE);
								bytesExtraOffset = write_result % SAMPLE_SIZE;
							}
							else { //Wrote full packet
								sampleCounter = 0;
								bytesExtraOffset = 0;
							}
						}

						//If buffer is not full but send is available still try sending data
						//else if (sampleCounter % 10 == 0)
						else if (0 && select( mSocket + 1, NULL , &fds, NULL, &tv ) > 0) 
						{
							pkt_part_ctr += 1;
							unsigned int sizeOfPacket = (sampleCounter*SAMPLE_SIZE) + bytesExtraOffset;
							write_result = write(mSocket, inbufBig, sizeOfPacket);
							if(write_result > 0)
							{
								if(sizeOfPacket != write_result)
								{ 
									pkt_partial_write_ctr_3 += 1;
									memmove(inbufBig, (inbufBig + write_result), (sizeOfPacket - write_result));
									sampleCounter = sampleCounter - ((write_result + SAMPLE_SIZE - 1)/ SAMPLE_SIZE);
									bytesExtraOffset = write_result % SAMPLE_SIZE;
								}
								else
								{
									sampleCounter = 0;
									bytesExtraOffset = 0;
								}
								continue;
							}
							//TODO - Account for partial write that doesn't even send whole packet - is this needed?

							//This should never happen (we are "select"ing before hand so should not be errors)
							else
							{
								printf("ERROR 404");    
							}                         
						}

						//total_tx += write_result;
						//total_tx += inWaiting;
						//if (c++ % 500 == 0){
						//    printf("qs: %d\n",total_tx);
						//    total_tx = 0;
						//}

						//printf("select af: %d \n\n", select( mSocket + 1, NULL , &fds, NULL, &tv ));
						//while( select( mSocket + 1, NULL , &fds, NULL, &tv ) > 0){
						//    c++;
						//    vTaskDelay( 1 / portTICK_PERIOD_MS); // should send at 100 Hz
						//}
						//printf("Delayed for %d loops",c);


						/**
						  When non-block writing with no SELECT checker, 
						  write_result evenetually == -1, then the following 
						  block closes out the streaming loop.
						 **/
					}
				}
			}
			nbset = 0;
			ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
			printf("set blocking: %d\n", ctlr);
			ads->stopStreaming();
		}

		int _read_ready(bool check_alive){

			// Periodically check connection
			// Set counter to 5.2E3 for 20KBps tx rate (w/o serial printing)
			if (check_alive && (mKeepAliveCounter++ > 5E3)){
				mKeepAliveCounter = 0;
				// TODO remove this outer for loop
				int retry_counter = 0;
				int result = -1;
				static int retry_total = 0;

				test_outbuf[0] = 'x';
				test_outbuf[1] = 'x';
				test_outbuf[2] = 'x';
				test_outbuf[3]++;
				test_outbuf[4] = 'y';
				test_outbuf[5] = 'y';
				test_outbuf[6] = 'y';

				if(false) { //JCR
					while (result = write(mSocket, test_outbuf, TEST_BUF_LEN), result < 0){

						//vTaskDelay(10 / portTICK_PERIOD_MS);
						//if (retry_total++ % 100 == 0)
						//    printf("retry_total: %d\n",retry_total);
						//if (retry_counter++ < 10000)
						//    continue;

						//printf("Attempting to recover\n");
						//print_seg_queues(mSocket);

						//Make blocking
						int nbset = 0;
						int ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);

						taskYIELD();
						if (result = write(mSocket, test_outbuf, TEST_BUF_LEN), result < 0){
							printf("Failed to recover\n");
						}
						else {
							//printf("Succeeded to recover\n");
							//vTaskDelay(10 / portTICK_PERIOD_MS);
							nbset = 1;
							ctlr = lwip_ioctl(mSocket, FIONBIO, &nbset);
							break;
						}

						get_pool_sizes();
						printf("--------------\n");
						char wbuf[400] = {0};
						vTaskList(wbuf);
						printf(wbuf);
						printf("--------------\n");
						vTaskGetRunTimeStats(wbuf);
						printf(wbuf);
						printf("--------------\n");
						printf("retry_total: %d\n",retry_total);
						printf("heap size: %d\n", xPortGetFreeHeapSize());
						printf("failed to receive ACK");
						//stats_display();
						return -1;
					}
				}
				//tcp_output(mSocket
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

        void _stream_task(ADS* ads)
        {

            // Use this from main loop to launch stream task
            // OR simply run inside of main loop to avoid any task switching
            //xTaskCreate(&_stream_task, (signed char *)"udp_stream_task", 4096, NULL, 2, NULL);

            const int WEB_PORT = 50007;
            const int pkt_size = 1400;
            const int inbuf_size = 3;

            // Setup remote address
            struct addrinfo res;
            struct ip_addr my_host_ip;
            IP4_ADDR(&my_host_ip, 192, 168, 1, 168);
            struct sockaddr_in my_sockaddr_in = {

                .sin_addr.s_addr = my_host_ip.addr,
                .sin_len = sizeof(struct sockaddr_in),
                .sin_family = AF_INET,
                .sin_port = htons(WEB_PORT),
                .sin_zero = 0        
            };

            res.ai_addr = (struct sockaddr*) (void*)(&my_sockaddr_in);
            res.ai_addrlen = sizeof(struct sockaddr_in);
            res.ai_family = AF_INET;
            res.ai_socktype = SOCK_DGRAM;

            // Setup local address
            struct addrinfo res_x;
            struct sockaddr_in my_sockaddr_x = {

                .sin_addr.s_addr = htonl(INADDR_ANY), // Binding local addr
                .sin_len = sizeof(struct sockaddr_in),
                .sin_family = AF_INET,
                .sin_port = htons(WEB_PORT),
                .sin_zero = 0        
            };

            res_x.ai_addr = (struct sockaddr*) (void*)(&my_sockaddr_x);
            res_x.ai_addrlen = sizeof(struct sockaddr_in);
            res_x.ai_family = AF_INET;
            res_x.ai_socktype = SOCK_DGRAM;

            while(1) {

                // Allocated socket
                int s = socket(res_x.ai_family, res_x.ai_socktype, 0);
                if(s < 0) {
                    printf("... Failed to allocate socket.\r\n");
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }
                printf("... allocated socket\r\n");

                // Bind local socket
                if(bind(s, res_x.ai_addr, res_x.ai_addrlen) < 0) {
                    close(s);
                    printf("bind failed.\r\n");
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                    continue;
                }
                printf("... bind success\r\n");

                // Init stream variables
                char outbuf[pkt_size] = {0};
                char inbuf[inbuf_size] = {0};
                uint8_t pkt_cnt = 0;
                uint8_t drop_count = 0;
                bool local_buf_acked = true;

                /******************************** 
                 Main stream loop
                 *********************************/

                while(1) {

                    // If new data in local buf, send it
                    if (!local_buf_acked) {
                        if (sendto(s, outbuf, pkt_size, 0, res.ai_addr, &(res.ai_addrlen) ) < 0) {
                            printf("... socket send failed\r\n");
                            close(s);
                            break;
                        }
                    }
                    
                    // If local buf is free, check queue for new packet's worth of data
                    if (local_buf_acked){
                        if (ads->getQueueSize() >= 57){
                            // Fill local buffer with new data
                            if (ads->getDataPacket(outbuf)){ 
                                local_buf_acked = false;
                                outbuf[0] = pkt_cnt;
                            }
                            else{
                                printf("Failed to load outbuf, file: %s, line: %d\n",__FILE__,__LINE__);
                            }
                    }

                    // Blocking read for ACK on currently buffered packet
                    // TODO ADS interrupt should be running during this time, "blocking" read needs to allow gpio interrupt to take priority
                    // TODO if this is a problem, we can use non-blocking read with a select() check, taskYIELD(), and read flash which only sends packet if we've received another ack
                    recvfrom(s, inbuf, inbuf_size, 0, res.ai_addr, &(res.ai_addrlen)); 
                    if (inbuf[0] == outbuf[0])
                    {
                        // It's a proper ACK, move to next packet
                        outbuf[0] = pkt_cnt++;
                        local_buf_acked = true;
                    }
                    else  {
                        else if (inbuf[3] == 0xff){
                            printf("Received TERMINATE command\n");
                            return;
                        }
                        drop_count++;
                    }
                }
            }
        }
};
