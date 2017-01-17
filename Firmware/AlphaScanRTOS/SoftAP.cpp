#include <string.h>
#include <espressif/esp_common.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <dhcpserver.h>
#include <lwip/api.h>
#include <cstring>

#define TELNET_PORT 23
const char* AP_SSID = "esp-open-rtos AP";
char AP_PSK[11] = "hello-moto";

class SoftAP {

    public:  

        void initialize(void)
        {
            printf("initializing SoftAP");

            sdk_wifi_set_opmode(SOFTAP_MODE);

            printf("Set opmode success");

            struct ip_info ap_ip;
            IP4_ADDR(&ap_ip.ip, 172, 16, 0, 1);
            IP4_ADDR(&ap_ip.gw, 0, 0, 0, 0);
            IP4_ADDR(&ap_ip.netmask, 255, 255, 0, 0);
            sdk_wifi_set_ip_info(1, &ap_ip);

            printf("Set ip info success");

            struct sdk_softap_config ap_config;

            printf("declared ap_config");

            memcpy(ap_config.ssid, AP_SSID, strlen((const char*) AP_SSID));
            memcpy(ap_config.password, AP_PSK, 11);
            //memcpy(ap_config.password, "password_fartman", strlen("password_fartman"));

            //strncpy(ap_config.ssid, reinterpret_cast<char*>(AP_SSID), sizeof(AP_SSID));
            //strncpy(ap_config.password, reinterpret_cast<char*>(AP_PSK),  sizeof(AP_PSK));
    //        strcpy(ap_config.ssid, "fart_haus");
      //      strcpy(ap_config.password, "stooooopid");
//            strncpy(ap_config.ssid, AP_SSID, sizeof(AP_SSID));
//            strncpy(ap_config.password, AP_PSK,  sizeof(AP_PSK));

            printf("Completed reinterpret cast");

            ap_config.ssid_len = strlen(AP_SSID);
            ap_config.channel = 3;
            ap_config.authmode = AUTH_WPA_WPA2_PSK;
            ap_config.ssid_hidden = 0;
            ap_config.max_connection = 3;
            ap_config.beacon_interval = 100;

            printf("Created config struct");

            sdk_wifi_softap_set_config(&ap_config);

            printf("Set soft ap config success");

            ip_addr_t first_client_ip;
            IP4_ADDR(&first_client_ip, 172, 16, 0, 2);
            dhcpserver_start(&first_client_ip, 4);

            printf("Init complete... initializing telnet task");

            //           xTaskCreate(telnetTask, (const char *)"telnetTask", 512, NULL, 2, NULL);
            //telnetTask(NULL);
        }

        /* Telnet task listens on port 23, returns some status information and then closes
           the connection if you connect to it.
         */
        static void telnetTask(void *pvParameters)
        {

            printf("inside telnet task");

            struct netconn *nc = netconn_new (NETCONN_TCP);
            if(!nc) {
                printf("Status monitor: Failed to allocate socket.\r\n");
                return;
            }
            netconn_bind(nc, IP_ADDR_ANY, TELNET_PORT);
            netconn_listen(nc);

            while(1) {
                struct netconn *client = NULL;
                err_t err = netconn_accept(nc, &client);

                if ( err != ERR_OK ) {
                    if(client)
                        netconn_delete(client);
                    continue;
                }

                ip_addr_t client_addr;
                uint16_t port_ignore;
                netconn_peer(client, &client_addr, &port_ignore);

                char buf[80];
                snprintf(buf, sizeof(buf), "Uptime %d seconds\r\n",
                        xTaskGetTickCount()*portTICK_PERIOD_MS/1000);
                netconn_write(client, buf, strlen(buf), NETCONN_COPY);
                snprintf(buf, sizeof(buf), "Free heap %d bytes\r\n", (int)xPortGetFreeHeapSize());
                netconn_write(client, buf, strlen(buf), NETCONN_COPY);
                snprintf(buf, sizeof(buf), "Your address is %d.%d.%d.%d\r\n\r\n",
                        ip4_addr1(&client_addr), ip4_addr2(&client_addr),
                        ip4_addr3(&client_addr), ip4_addr4(&client_addr));
                netconn_write(client, buf, strlen(buf), NETCONN_COPY);
                netconn_delete(client);
            }
        }
};
