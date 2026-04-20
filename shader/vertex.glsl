#version 400
layout(location = 0) in vec3 vertex_posicao;
layout(location = 1) in vec3 vertex_normal;
layout(location = 2) in vec4 vertex_color;   // usado apenas no modo batch

uniform mat4 transform, view, proj;
uniform int  use_vertex_color;                // 1 = batch (cor no VBO), 0 = uniforme

out vec3 world_normal;
out vec4 v_color;

void main () {
    gl_Position  = proj * view * transform * vec4(vertex_posicao, 1.0);
    world_normal = mat3(transform) * vertex_normal;
    v_color      = vertex_color;
}
