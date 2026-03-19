exit
su
sudo su
yum update -y
ifconfig
ipconfig
ip a
systemctl status firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload
firewall-cmd --list-all
firewall-cmd --reloadsudo -i
sudo -i
service firewalld status
systemctl restart firewalld
systemctl status firewalld
systemctl enable firewalld
firewall-cmd --lista-all
firewall-cmd --list-all
systemctl status firewalld
root
docker-compose --version
docker network create bot_network
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
docker-compose --version
docker compose version
docker ps
docker run -d   --name telegram_postgres   --network bot_network   -e POSTGRES_USER=bot_user   -e POSTGRES_PASSWORD=bot_password   -e POSTGRES_DB=bot_db   -p 5432:5432   -v pgdata:/var/lib/postgresql/data   postgres:15
ll
cd /home
ll
su devops/
nano docker-compose.yml
docker-compose up -d
docker ps
docker exec -it telegram_postgres psql -U bot_user -d bot_db
docker ps
