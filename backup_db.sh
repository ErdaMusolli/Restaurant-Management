docker exec -t restaurant_db pg_dumpall -c -U restaurant_user > backup_$(date +%F).sql
echo "Backup completed: backup_$(date +%F).sql"
