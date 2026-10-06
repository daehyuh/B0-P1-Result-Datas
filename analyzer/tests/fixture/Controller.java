import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

class Controller {
    private final Service service = new Service();

    @GetMapping("/items/{id}")
    String item(@PathVariable String id) {
        return service.find(id);
    }
}
