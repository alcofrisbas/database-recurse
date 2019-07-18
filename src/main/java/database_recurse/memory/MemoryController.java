package database_recurse.memory;

import java.util.*;


import org.json.simple.JSONObject;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MemoryController{
    private Map memoryMap;

    public MemoryController() {
        this.memoryMap = new HashMap<String,String>();
    }

    @RequestMapping(path="/set")
    public JSONObject setValue(@RequestParam Map<String, String> attMap){
        //do logic here!
        this.memoryMap.putAll(attMap);

        JSONObject jso = new JSONObject();
        jso.put("msg", "sucess");
        return jso;
    }

    @RequestMapping(path="/get")
    public JSONObject getValue(@RequestParam (value="key")String key){
        String value = (String)this.memoryMap.getOrDefault(key, null);
        JSONObject jso = new JSONObject();
        jso.put(key,value);
        return jso;
    }
}