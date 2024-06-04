import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.util.Timer;
import java.util.TimerTask;

public class SolarCar {
    static { System.loadLibrary(Core.NATIVE_LIBRARY_NAME); }

    private JFrame frame;
    private JLabel videoLabel;
    private JLabel speedLabel;
    private JLabel distanceLabel;
    private JLabel tempLabel;
    private JLabel timeLabel;
    private JLabel serialDataLabel;
    private VideoCapture videoCapture;
    private Timer timer;
    private double startTime;
    private double oneCycleLen;
    private int rotCounter;
    private int previousState;
    private double distance;
    private double previousDistance;
    private boolean isKm;

    public SolarCar() {
        frame = new JFrame("Kent Solar Car");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1920, 1080);
        frame.setLayout(null);

        videoLabel = new JLabel();
        videoLabel.setBounds(0, 0, 1920, 1080);
        frame.add(videoLabel);

        speedLabel = new JLabel("Speed: ", JLabel.LEFT);
        speedLabel.setFont(new Font("Arial", Font.PLAIN, 45));
        speedLabel.setBounds(20, 30, 500, 50);
        frame.add(speedLabel);

        distanceLabel = new JLabel("Distance: ", JLabel.LEFT);
        distanceLabel.setFont(new Font("Arial", Font.PLAIN, 45));
        distanceLabel.setBounds(20, 100, 500, 50);
        frame.add(distanceLabel);

        tempLabel = new JLabel("Temperature: ", JLabel.LEFT);
        tempLabel.setFont(new Font("Arial", Font.PLAIN, 45));
        tempLabel.setBounds(20, 170, 500, 50);
        frame.add(tempLabel);

        timeLabel = new JLabel("Time: ", JLabel.LEFT);
        timeLabel.setFont(new Font("Arial", Font.PLAIN, 45));
        timeLabel.setBounds(20, 240, 500, 50);
        frame.add(timeLabel);

        serialDataLabel = new JLabel("", JLabel.LEFT);
        serialDataLabel.setFont(new Font("Arial", Font.PLAIN, 45));
        serialDataLabel.setBounds(20, 310, 500, 50);
        frame.add(serialDataLabel);

        frame.setVisible(true);

        videoCapture = new VideoCapture(0);
        timer = new Timer();
        startTime = System.currentTimeMillis();
        oneCycleLen = 2.153412;
        rotCounter = 0;
        previousState = 1;
        distance = 0;
        previousDistance = 0;
        isKm = true;

        startLoop();
    }

    private void startLoop() {
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                update();
            }
        }, 0, 33); // Update at ~30 FPS

        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                updateSpeed();
            }
        }, 0, 1000); // Update speed every second

        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                updateDistance();
            }
        }, 0, 1); // Update distance continuously

        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                updateTemp();
            }
        }, 0, 1000); // Update temperature every second

        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                updateTime();
            }
        }, 0, 500); // Update time every half second
    }

    private void update() {
        Mat frame = new Mat();
        if (videoCapture.read(frame)) {
            Imgproc.cvtColor(frame, frame, Imgproc.COLOR_BGR2RGBA);
            ImageIcon image = new ImageIcon(matToBufferedImage(frame));
            videoLabel.setIcon(image);
        }
    }

    private BufferedImage matToBufferedImage(Mat mat) {
        int type = BufferedImage.TYPE_BYTE_GRAY;
        if (mat.channels() > 1) {
            type = BufferedImage.TYPE_3BYTE_BGR;
        }
        BufferedImage image = new BufferedImage(mat.cols(), mat.rows(), type);
        mat.get(0, 0, ((DataBufferByte) image.getRaster().getDataBuffer()).getData());
        return image;
    }

    private void updateSpeed() {
        double timePassed = 1.0 / 3600.0; // 1 hour in seconds
        double distanceCovered = (distance - previousDistance) / 1000.0; // km
        double currentSpeed = distanceCovered / timePassed;
        if (isKm) {
            speedLabel.setText(String.format("Speed: %.2f kmph", currentSpeed));
        } else {
            speedLabel.setText(String.format("Speed: %.2f mph", currentSpeed / 1.61));
        }
        previousDistance = distance;
    }

    private void updateDistance() {
        int x = getTouch();
        if (previousState != x && previousState == 1) {
            rotCounter++;
        }
        previousState = x;
        distance = rotCounter * oneCycleLen / 1000.0;
        if (isKm) {
            distanceLabel.setText(String.format("Distance: %.3f km", distance));
        } else {
            distanceLabel.setText(String.format("Distance: %.3f miles", distance / 1.61));
        }
    }

    private void updateTemp() {
        double c = getTemp();
        double f = c * 9.0 / 5.0 + 32.0;
        tempLabel.setText(String.format("Temperature: %.2f C | %.2f F", c, f));
    }

    private void updateTime() {
        double elapsedTime = (System.currentTimeMillis() - startTime) / 60000.0; // minutes
        timeLabel.setText(String.format("Time: %.2f min", elapsedTime));
    }

    private int getTouch() {
        // Implement touch sensor reading logic
        return 1; // Placeholder
    }

    private double getTemp() {
        // Implement temperature reading logic
        return 25.0; // Placeholder
    }

    public static void main(String[] args) {
        new SolarCar();
    }
}