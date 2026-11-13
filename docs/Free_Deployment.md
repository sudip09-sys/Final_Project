# Free cloud deployment

The intended free configuration uses Render Free for the Docker web service and a TiDB Cloud Starter MySQL-compatible database. TiDB is a different database implementation from MySQL; the local Docker Compose configuration continues to run actual MySQL 8.4.

Keep the TiDB spending limit at zero and the Render service plan on Free. Free quotas and availability are controlled by the providers. Render Free sleeps after inactivity and its local filesystem is temporary.

## Live demo and administrator sign-in

- Application: https://attendly-sudip.onrender.com/
- Render service: https://dashboard.render.com/web/srv-dbrfnq3bc2fs73cupdtg
- Open the service's **Environment** tab and reveal `INITIAL_ADMIN_PASSWORD` to obtain your generated application password. Provider login credentials are never needed in the application.
- The application verifies `ADMIN_PASSWORD_HASH`; `INITIAL_ADMIN_PASSWORD` is a delivery secret kept in Render's environment settings. Remove that delivery variable after securely saving your password. Keep the hash and embedding key unchanged.

Current status: the HTTPS demo is live and uses temporary SQLite storage. Persistent TiDB storage remains pending. A closed **Deployment check** session records the automated smoke test; its temporary test student and attendance were deleted.

## Persistent database setup

1. Create a TiDB **Starter**, **MySQL Compatible** instance with spending limit **0**. Use a nearby region.
2. Open its **Connect** panel and obtain the SQLAlchemy/PyMySQL connection URL. Use `mysql+pymysql://`, port `4000`, and the existing database name supplied by TiDB (usually `test`). Alternatively, create a separate database named `attendance` and use that. URL-encode password characters. The application creates its tables on startup.
3. In the Render service's **Environment** settings, enter the URL directly as the secret `DATABASE_URL`. Do not post it in a chat or commit it.
4. Keep `DATABASE_TLS=1`. The application uses the system certificate authorities and verifies the database certificate and hostname.
5. Save and deploy. After login, the temporary-storage notice must be absent. Verify attendance still exists after restarting the service.

Until the persistent connection is configured, a Render demo using SQLite displays a permanent warning that records reset on service restart. Export CSV before leaving. A running SQLite demo does not establish that the persistent deployment is complete.

Do not change `SECRET_KEY` or `EMBEDDING_KEY` during a normal deployment. Rotating the embedding key without migrating templates makes existing templates unreadable.
