package bm.iot.garage;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

public class PollutionCircleView extends View {

    private int pollutionValue;
    private Paint paint;

    public PollutionCircleView(Context context) {
        super(context);
        init();
    }

    public PollutionCircleView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public PollutionCircleView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        paint = new Paint();
        paint.setAntiAlias(true);
    }

    public void setPollutionValue(int pollutionValue) {
        this.pollutionValue = pollutionValue;
        invalidate(); // Redraw the view to update the color
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Get the view dimensions
        int width = getWidth();
        int height = getHeight();

        // Calculate the radius of the inner and outer circles
        int radius1 = width / 2;
        int radius2 = (int) (radius1 * 0.8);

        // Set the color of the outer circle based on the pollution value
        if (pollutionValue <= 1750) {
            paint.setColor(Color.GREEN);
        } else if (pollutionValue <= 2250) {
            paint.setColor(Color.YELLOW);
        } else  {
            paint.setColor(Color.RED);
        }

        // Draw the outer circle
        canvas.drawCircle(width / 2, height / 2, radius1, paint);

        // Set the color of the inner circle to white
        paint.setColor(Color.WHITE);

        // Draw the inner circle
        canvas.drawCircle(width / 2, height / 2, radius2, paint);

        // Draw the pollution value text in the center of the view
        paint.setColor(Color.BLACK);
        paint.setTextSize((int) (radius2 * 0.8));
        paint.setTextAlign(Paint.Align.CENTER);
        canvas.drawText(String.valueOf(pollutionValue), width / 2, height / 2 + (int) (radius2 * 0.7) / 2, paint);
    }
}

