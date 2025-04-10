# Start with the official MySQL 5.7 image
FROM mysql:5.7

# Copy the custom MySQL configuration file to the container
COPY ./my.cnf /etc/mysql/my.cnf

# Set environment variable to avoid running in interactive mode
ENV MYSQL_ROOT_PASSWORD=somepassword

# Expose MySQL port
EXPOSE 3306

# Run the MySQL server (entrypoint is already defined in the MySQL base image)
CMD ["mysqld"]