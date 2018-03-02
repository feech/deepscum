package deepscum.ik;

import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.dao.DataAccessException;
import org.springframework.data.annotation.Id;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.jedis.JedisConnectionFactory;
import org.springframework.data.redis.core.*;
import org.springframework.data.redis.serializer.RedisSerializer;
import org.springframework.data.repository.CrudRepository;
import org.springframework.web.bind.annotation.*;

import javax.json.*;
import javax.json.stream.JsonGenerator;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.logging.Logger;

/**
 * Hello world!
 */
@SpringBootApplication
public class App {
    public static void main(String[] args) {

        SpringApplication.run(App.class, args);
    }
}


@RedisHash("survey")
class Survey {

    @Id
    String id;
    String date;

}

interface SurveyRepository extends CrudRepository<Survey, String> {

}


@RestController
@RequestMapping("/api")
class OutData {

    private static Logger LOG = Logger.getLogger("OutData");

    @Autowired
    SurveyRepository surveyRepository;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    @Autowired
    private RedisTemplate<String, byte[]> template;

    @Autowired
    JedisConnectionFactory jedisConnectionFactory;

    @GetMapping("/hello")
    String hello() {
        return "hello";
    }

    @GetMapping(path = "/screen-number")
    String getScreenNumber() {
        return stringRedisTemplate.boundValueOps("surveys:images").get();
    }

    /**
     * get latest image from fs
     *
     * @param response
     * @throws IOException
     */
    @GetMapping(path = "/screen")
    void getScreen(HttpServletResponse response) throws IOException {

        final String image_id = stringRedisTemplate.opsForValue().get("surveys:images");

        byte[] image = getImage(image_id);

        if (image == null) {
            response.setStatus(404);
            return;
        }


        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(image);
        response.setContentType("image/png");
        IOUtils.copy(byteArrayInputStream, response.getOutputStream());
    }

    /**
     * return null if notFound
     *
     * @param image_id
     * @return
     */
    private byte[] getImage(final String image_id) {
        return template.execute(new RedisCallback<byte[]>() {
            @Override
            public byte[] doInRedis(RedisConnection redisConnection) throws DataAccessException {
                Cursor<byte[]> scan = redisConnection.scan(ScanOptions.scanOptions().match("survey:*:image:" + image_id + ":data").build());
                if (!scan.hasNext()) {
                    return null;
                }
                byte[] key = scan.next();
                return redisConnection.get(key);
            }
        });
    }


    @GetMapping(path = "/image/{image_id}/info", produces = "application/json")
    Map<String, String> getImageInfo(@PathVariable("image_id") String image_id) {

        final String skey = "survey:*:image:" + image_id + ":*";
        final RedisSerializer<String> stringSerializer = stringRedisTemplate.getStringSerializer();

        Map<String, String> res = stringRedisTemplate.execute(new RedisCallback<Map<String, String>>() {
            @Override
            public Map<String, String> doInRedis(RedisConnection connection) throws DataAccessException {
                Cursor<byte[]> scan = connection.scan(ScanOptions.scanOptions().match(skey).build());
                if (!scan.hasNext()) {
                    return null;
                }
                Map<String, String> res = new TreeMap<String, String>();
                String survey = null;
                while (scan.hasNext()) {
                    byte[] key = scan.next();
                    String[] key_parts = stringSerializer.deserialize(key).split(":");
                    if (survey == null) {
                        survey = key_parts[1];
                        res.put("survey", survey);
                    }
                    if ("data".equals(key_parts[key_parts.length - 1])) {
                        continue;
                    }
                    byte[] value = connection.get(key);
                    res.put(key_parts[key_parts.length - 1], stringSerializer.deserialize(value));
                }
                return res;
            }
        });


        if (res == null) {
            throw new RuntimeException("NotFound");
        }
        res.put("id", image_id);
        return res;
    }

    @GetMapping(path = "/image/{image_id}")
    void getImage(@PathVariable("image_id") String image_id,
                  HttpServletResponse response) throws IOException {

        byte[] image = getImage(image_id);
        if (image == null) {
            response.setStatus(404);
            return;
        }

        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(image);
        response.setContentType("image/png");
        IOUtils.copy(byteArrayInputStream, response.getOutputStream());

    }

    @PostMapping(path = "/image/{image_id}/class")
    void setImageClass(@PathVariable("image_id") String image_id,
                       @RequestParam("class") String className) {
        Map<String, String> imageInfo = getImageInfo(image_id);
        stringRedisTemplate.opsForValue().set("survey:" + imageInfo.get("survey") + ":image:" + image_id + ":class", className);
    }


    @PostMapping(path = "/image/{image_id}/input")
    void input(@PathVariable("image_id") String image_id,
               @RequestBody InputShape inputShape
//               @RequestParam(value = "l", required = false) String left,
//               @RequestParam(value = "t", required = false) String top,
//               @RequestParam("w") String w,
//               @RequestParam("h") String h,
//               @RequestParam("component") String component
    ) {
        Map<String, String> imageInfo = getImageInfo(image_id);

        JsonArray jsonArray;
        String input = imageInfo.get("input");
        if (input == null || input.isEmpty()) {
            jsonArray = Json.createArrayBuilder().build();
        } else {
            try (JsonReader rdr = Json.createReader(new StringReader(input))) {
                jsonArray = rdr.readArray();
            }
        }

        Optional<JsonValue> hit = jsonArray.stream().filter(x -> hit(x, inputShape)).findFirst();


        StringWriter sw = new StringWriter();
        if (hit.isPresent()) {
            JsonObjectBuilder objectBuilder = Json.createObjectBuilder();
            if (hit.get().asJsonObject().get("l") != null)
                objectBuilder.add("l", hit.get().asJsonObject().getString("l"));
            if (hit.get().asJsonObject().get("t") != null)
                objectBuilder.add("t", hit.get().asJsonObject().getString("t"));
            if (hit.get().asJsonObject().get("w") != null)
                objectBuilder.add("w", hit.get().asJsonObject().getString("w"));
            if (hit.get().asJsonObject().get("h") != null)
                objectBuilder.add("h", hit.get().asJsonObject().getString("h"));
            if (inputShape.x != null)
                objectBuilder.add("x", inputShape.getX());
            if (inputShape.y != null)
                objectBuilder.add("y", inputShape.getY());
            if (hit.get().asJsonObject().get("component") != null)
                objectBuilder.add("component", hit.get().asJsonObject().getString("component"));

            try (JsonGenerator generator = Json.createGenerator(sw)) {
                generator.writeStartArray();
                jsonArray.stream().filter(x -> !hit(x, inputShape)).forEach(generator::write);
                generator.write(objectBuilder.build()).writeEnd();
            }
        } else {
            JsonObjectBuilder objectBuilder = Json.createObjectBuilder();
            if (inputShape.l != null)
                objectBuilder.add("l", inputShape.l);
            if (inputShape.t != null)
                objectBuilder.add("t", inputShape.t);
            if (inputShape.w != null)
                objectBuilder.add("w", inputShape.w);
            if (inputShape.h != null)
                objectBuilder.add("h", inputShape.h);
            if (inputShape.x != null)
                objectBuilder.add("x", inputShape.x);
            if (inputShape.y != null)
                objectBuilder.add("y", inputShape.y);
            if (inputShape.component != null)
                objectBuilder.add("component", inputShape.component);

            try (JsonGenerator generator = Json.createGenerator(sw)) {

                generator.writeStartArray();
                jsonArray.forEach(generator::write);
                generator.write(objectBuilder.build()).writeEnd();
            }
        }

        String s = sw.getBuffer().toString();
        System.out.println(s);
        stringRedisTemplate.opsForValue().set("survey:" + imageInfo.get("survey") + ":image:" + image_id + ":input", s);

    }

    @DeleteMapping(path = "/image/{image_id}/input")
    void inputLastDelete(@PathVariable("image_id") String image_id) {
        Map<String, String> imageInfo = getImageInfo(image_id);

        JsonArray jsonValues;
        String input = imageInfo.get("input");
        if (input == null || input.isEmpty()) {
            return;
        }

        try (JsonReader rdr = Json.createReader(new StringReader(input))) {
            jsonValues = rdr.readArray();
        }

        if (jsonValues.size() < 2) {
            stringRedisTemplate.opsForValue().set("survey:" + imageInfo.get("survey") + ":image:" + image_id + ":input", "");
            return;
        }

        StringWriter sw = new StringWriter();
        try (JsonGenerator generator = Json.createGenerator(sw)) {

            generator.writeStartArray();
            jsonValues.stream()
                    .limit(jsonValues.size() - 1L)
                    .forEach(generator::write);
            generator.writeEnd();
        }

        String s = sw.getBuffer().toString();
        System.out.println(s);
        stringRedisTemplate.opsForValue().set("survey:" + imageInfo.get("survey") + ":image:" + image_id + ":input", s);

    }

    static Integer extract(JsonValue v, String nm) {
        if (v.asJsonObject().get(nm) == null ) {
            return null;
        }
        return Integer.parseInt(v.asJsonObject().getString(nm));
    }

    static boolean hit(JsonValue v, InputShape inputShape) {
        if (inputShape.getX() == null || inputShape.getY() == null) {
            return false;
        }

        Integer cx = Integer.parseInt(inputShape.getX());
        Integer cy = Integer.parseInt(inputShape.getY());


        Integer l = extract(v, "l");
        Integer t = extract(v, "t");
        Integer w = extract(v, "w");
        Integer h = extract(v, "h");
        Integer x = extract(v, "x");
        Integer y = extract(v, "y");

        // check area with l,t,w,h
        if (l != null && t != null && w != null && h != null) {
            return l < cx && (l + w) > cx && t < cy && (t + h) > cy;
        }
        // check area with x,y,w,h
        if (x != null && y != null && w != null && h != null) {
            return (x + w / 2 - w) < cx && (x + w / 2) > cx && (y + h / 2 - h) < cy && (y + h / 2) > cy;
        }
        return false;
    }
}

class InputShape {
    String l;
    String t;
    String w;
    String h;
    String component;
    String x;
    String y;


    public String getL() {
        return l;
    }

    public void setL(String l) {
        this.l = l;
    }

    public String getT() {
        return t;
    }

    public void setT(String t) {
        this.t = t;
    }

    public String getW() {
        return w;
    }

    public void setW(String w) {
        this.w = w;
    }

    public String getH() {
        return h;
    }

    public void setH(String h) {
        this.h = h;
    }

    public String getComponent() {
        return component;
    }

    public void setComponent(String component) {
        this.component = component;
    }

    public String getX() {
        return x;
    }

    public void setX(String x) {
        this.x = x;
    }

    public String getY() {
        return y;
    }

    public void setY(String y) {
        this.y = y;
    }
}