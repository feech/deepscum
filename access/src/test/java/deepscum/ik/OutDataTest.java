package deepscum.ik;

import org.junit.Test;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonValue;
import javax.json.stream.JsonGenerator;

import java.io.StringWriter;

import static org.junit.Assert.*;

/**
 * Created by Kirill on 2/28/2018.
 */
public class OutDataTest {

    @Test
    public void emptyFieldtoJsonString() {
////        InputShape inputShape = new InputShape();
//        String s = null;
//        JsonValue obj = Json.createObjectBuilder().add("ttt", s).build();
//
//        StringWriter sw = new StringWriter();
////        JsonArray jsonValues = Json.createArrayBuilder().build();
//        try (JsonGenerator generator = Json.createGenerator(sw)) {
//
//            generator.writeStartArray();
////            jsonValues.forEach(x -> generator.write(x));
//            generator.write(obj).writeEnd();
//        }
//
        assertEquals(1L, (long) Integer.getInteger("1"));
        assertNull(Integer.getInteger(null));
    }

}