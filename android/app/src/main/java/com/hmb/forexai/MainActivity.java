package com.hmb.forexai;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {

    private final Handler handler = new Handler();
    private TextView statusText;

    private static final String API =
            "https://hmb-forex-ai.fly.dev/healthz";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(35, 45, 35, 35);
        root.setBackgroundColor(Color.rgb(8, 8, 8));

        TextView title = text(
                "HMB FOREX AI",
                28
        );

        TextView mode = text(
                "PAPER ONLY  •  REAL ORDERS: OFF",
                15
        );

        statusText = text(
                "Connecting...",
                16
        );

        root.addView(title);
        root.addView(mode);
        root.addView(statusText);

        setContentView(root);

        refresh();
    }

    private TextView text(String value, int size) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextColor(Color.WHITE);
        t.setTextSize(size);
        t.setGravity(Gravity.CENTER_HORIZONTAL);
        t.setPadding(0, 20, 0, 20);
        return t;
    }

    private void refresh() {

        new Thread(() -> {

            try {

                URL url = new URL(API);

                HttpURLConnection connection =
                        (HttpURLConnection) url.openConnection();

                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);

                BufferedReader reader =
                        new BufferedReader(
                                new InputStreamReader(
                                        connection.getInputStream()
                                )
                        );

                StringBuilder response =
                        new StringBuilder();

                String line;

                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }

                reader.close();

                JSONObject json =
                        new JSONObject(response.toString());

                String price =
                        json.optString(
                                "last_price",
                                "-"
                        );

                String signal =
                        json.optString(
                                "last_signal",
                                "WAIT"
                        );

                String update =
                        json.optString(
                                "last_update",
                                "-"
                        );

                String result =
                        "EURUSD\n\n"
                        + "PRICE: " + price
                        + "\n\n"
                        + "SIGNAL: " + signal
                        + "\n\n"
                        + "LAST UPDATE:\n"
                        + update
                        + "\n\n"
                        + "PAPER TRADING\n"
                        + "REAL ORDERS: OFF";

                runOnUiThread(() ->
                        statusText.setText(result)
                );

            } catch (Exception e) {

                runOnUiThread(() ->
                        statusText.setText(
                                "Connection error\n\n"
                                + e.getMessage()
                        )
                );
            }

        }).start();

        handler.postDelayed(
                this::refresh,
                60000
        );
    }
}
