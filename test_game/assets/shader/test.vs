
// attribute vec2 a_position;
// attribute vec4 a_position;
// attribute vec2 a_texCoord0;

varying vec2 v_texCoords;


// void main ()
// {
// 	gl_Position = a_position;
// 	v_texCoords = a_texCoord0;
// }

void main()
{
    vec4 position = gl_ModelViewProjectionMatrix * gl_Vertex;
 	v_texCoords = vec2(position.x, position.y);

    gl_Position = position;
}
