A veces en local gspread se queda pegado en la autenticación. Para arreglarlo hay que ejecutar el siguiente comando:
```bash
sysctl net.ipv6.conf.all.disable_ipv6=1
```