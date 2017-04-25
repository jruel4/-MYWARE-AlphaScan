#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "esp/spi.h"
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
#include "esp8266.h"

#define WEB_PORT 2050
#define pkt_size 8*5
#define inbuf_size 8*5

const int freq_frc1 = 1;
const int freq_frc2 = 1000;

void http_get_task(void *pvParameters)
{

    // Setup remote address
    struct addrinfo res;
    struct ip_addr my_host_ip;
    IP4_ADDR(&my_host_ip, 0, 0, 0, 0); // will be overwritten by recvfrom
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

        dump_heapinfo();

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

        char outbuf[pkt_size] = {0};
        uint8_t pkt_cnt = 0;
        uint8_t drop_count = 0;
        char inbuf[inbuf_size] = {0};
        uint8_t SYNC_TOKEN = 0x01;
        TickType_t lastWakeTime = xTaskGetTickCount();

        // Set blocking
        int nbset = 0;
        int ctlr = lwip_ioctl(s, FIONBIO, &nbset);
        uint64_t vals[5] = {0};

        //Send over WiFi
        while(1) {

            // Blocking recv from mntp server
            recvfrom(s, inbuf, inbuf_size, 0, res.ai_addr, &(res.ai_addrlen)); 

            // Generate t2
            uint32_t t2 = timer_get_count(FRC2) / 3;

            // Generate t3
            uint32_t t3 = timer_get_count(FRC2) / 3;

            // Copy t2
            int idx = 16;
            inbuf[idx++] = (t2>>0)&0xff;
            inbuf[idx++] = (t2>>8)&0xff;
            inbuf[idx++] = (t2>>16)&0xff;
            inbuf[idx++] = (t2>>24)&0xff;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;

            inbuf[idx++] = (t3>>0)&0xff;
            inbuf[idx++] = (t3>>8)&0xff;
            inbuf[idx++] = (t3>>16)&0xff;
            inbuf[idx++] = (t3>>24)&0xff;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;
            inbuf[idx++] = 0;


            // Send pkt 2
            if (sendto(s, inbuf, pkt_size, 0, res.ai_addr, &(res.ai_addrlen) ) < 0) {
                printf("... socket send failed\r\n");
                close(s);
                break;
            }
            printf("Processed request \n");
        }
    }
}

void user_init(void)
{
    uart_set_baud(0, 74880);
    printf("SDK version:%s\n", sdk_system_get_sdk_version());
    struct sdk_station_config config = {
        .ssid = WIFI_SSID,
        .password = WIFI_PASS,
    };
    sdk_wifi_set_opmode(STATION_MODE);
    sdk_wifi_station_set_config(&config);

    /* stop both timers and mask their interrupts as a precaution */
    timer_set_interrupts(FRC2, false);
    timer_set_run(FRC2, false);

    /* configure timer frequencies */
    timer_set_divider(FRC2, TIMER_CLKDIV_16);    

    /* unmask interrupts and start timers */
    timer_set_run(FRC2, true);

    xTaskCreate(&http_get_task, (signed char *)"get_task", 4096, NULL, 2, NULL);
}

