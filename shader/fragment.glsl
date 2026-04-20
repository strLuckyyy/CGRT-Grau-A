#version 400

in  vec3 world_normal;
in  vec4 v_color;
out vec4 frag_colour;

uniform vec4 colorobject;
uniform vec3 light_dir       = normalize(vec3(1.0, 1.0, 1.0));
uniform int  use_vertex_color;   // 1 = batch mode, 0 = uniforme mode

void main () {
    vec3  normal    = normalize(world_normal);
    float diffuse   = max(dot(normal, light_dir), 0.0);
    float ambient   = 0.3;
    float intensity = diffuse + ambient;

    vec4 base_color = (use_vertex_color == 1) ? v_color : colorobject;
    frag_colour     = vec4(base_color.rgb * intensity, base_color.a);
}
