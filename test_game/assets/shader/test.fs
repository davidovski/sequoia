// uniform sampler2D u_image;

varying vec2 v_texCoords;

void main ()
{
	// vec4 pointColour = texture2D(u_image, v_texCoords);

	vec4 pointColour = vec4(1.0, v_texCoords.x, v_texCoords.y, 1.0);
    gl_FragColor = pointColour;
}
