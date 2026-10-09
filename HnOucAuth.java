import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.InputStream;

/**
 * Runs on the phone via app_process. Talks to the stock framework class
 * android.hnouc.HnOucNative: dump getUpdateAuthParams, or saveUpdateAuth.
 */
public class HnOucAuth {
    public static void main(String[] args) throws Exception {
        exemptHiddenApi();
        if (args.length < 1) {
            System.out.println("usage: dump | save <response-file> <store-dir>");
            System.exit(2);
        }
        Class<?> cls = Class.forName("android.hnouc.HnOucNative");
        Object inst = cls.getMethod("getInstance").invoke(null);
        if (inst == null) {
            System.out.println("ERR getInstance null");
            System.exit(1);
        }
        if ("dump".equals(args[0])) {
            Object params = cls.getMethod("getUpdateAuthParams").invoke(inst);
            System.out.println("JSON " + params);
            return;
        }
        if ("save".equals(args[0])) {
            if (args.length < 3) {
                System.out.println("usage: save <response-file> <store-dir>");
                System.exit(2);
            }
            String response = readFile(args[1]);
            Object rc = cls.getMethod("saveUpdateAuth", String.class, String.class)
                    .invoke(inst, response, args[2]);
            System.out.println("RC " + rc);
            return;
        }
        System.out.println("ERR unknown command");
        System.exit(2);
    }

    private static void exemptHiddenApi() {
        try {
            Class<?> vm = Class.forName("dalvik.system.VMRuntime");
            Object runtime = vm.getMethod("getRuntime").invoke(null);
            vm.getMethod("setHiddenApiExemptions", String[].class)
                    .invoke(runtime, (Object) new String[] {"L"});
        } catch (Throwable ignored) {
        }
    }

    private static String readFile(String path) throws Exception {
        InputStream in = new FileInputStream(path);
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) >= 0) {
                bos.write(buf, 0, n);
            }
            return new String(bos.toByteArray(), "UTF-8");
        } finally {
            in.close();
        }
    }
}
