# Home Efficiency Study Integration

A custom integration for Home Assistant that allows you to report specific sensor state changes to an InfluxDB Cloud bucket, tagged with a unique House ID.

## Features

- **Native Configuration UI:** Easily configure your InfluxDB Cloud credentials directly from the Home Assistant dashboard.
- **Native Options UI:** Multi-select any number of existing entities from your Home Assistant instance to monitor and share.
- **Real-time Uploads:** Automatically pushes state changes of monitored entities to InfluxDB using Home Assistant's built-in event listener and async HTTP client.

## Installation

1. Download or copy the `efficiency_study` folder.
2. Place the `efficiency_study` folder inside the `custom_components` directory of your Home Assistant configuration (`/config/custom_components/efficiency_study`).
3. **Restart Home Assistant**.

## Configuration

1. In your Home Assistant dashboard, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Home Efficiency Study** and select it.
4. Provide the required InfluxDB Cloud credentials:
   - **InfluxDB Cloud URL**: Your InfluxDB URL (e.g., `https://us-east-1-1.aws.cloud2.influxdata.com`).
   - **API Token**: A token with write access to your chosen bucket.
   - **Organization**: Your InfluxDB Organization ID or Name.
   - **Bucket**: The target bucket to store the data.
   - **House ID**: A unique identifier for your home (this will be added as a tag to the metrics).
5. Click **Submit**.

## Selecting Sensors to Monitor

Once the initial configuration is complete, you need to select which sensors will share their data:
1. Locate the installed **Home Efficiency Study** integration in your integrations list under **Devices & Services**.
2. Click the **Configure** button on its card.
3. Select the entities you wish to share from the dropdown menu.
4. Click **Submit**.

The integration will automatically register listeners for the chosen entities and start uploading their state changes immediately!
