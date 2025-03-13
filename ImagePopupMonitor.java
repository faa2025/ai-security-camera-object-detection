import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.*;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;

public class ImagePopupMonitor {
    public static void main(String[] args) throws IOException, InterruptedException {
        String directoryPath = "recorded_media/saved_human_frame";  // Change this path to the directory you want to monitor
        Path dir = Paths.get(directoryPath);

        WatchService watchService = FileSystems.getDefault().newWatchService();
        dir.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);

        System.out.println("Monitoring directory: " + directoryPath);

        while (true) {
            WatchKey key = watchService.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                WatchEvent.Kind<?> kind = event.kind();
                if (kind == StandardWatchEventKinds.ENTRY_CREATE) {
                    Path filePath = dir.resolve((Path) event.context());
                    showImagePopup(filePath.toFile());
                }
            }
            key.reset();
        }
    }

    private static void showImagePopup(File imageFile) {
        Frame frame = new Frame();
        frame.setLayout(new BorderLayout());
        frame.setSize(600, 400);
        frame.setTitle("New Image Detected");

        try {
            BufferedImage img = ImageIO.read(imageFile);
            Image scaledImg = img.getScaledInstance(frame.getWidth(), frame.getHeight(), Image.SCALE_SMOOTH);
            Canvas canvas = new Canvas() {
                @Override
                public void paint(Graphics g) {
                    g.drawImage(scaledImg, 0, 0, this.getWidth(), this.getHeight(), this);
                }
            };
            frame.add(canvas, BorderLayout.CENTER);
        } catch (IOException e) {
            System.out.println("Failed to load image: " + e.getMessage());
            return;
        }

        frame.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                frame.dispose();
            }
        });

        frame.setVisible(true);

        // Close the window after 10 seconds
        new java.util.Timer().schedule(new java.util.TimerTask() {
            @Override
            public void run() {
                frame.dispose();
            }
        }, 10000);
    }
}

