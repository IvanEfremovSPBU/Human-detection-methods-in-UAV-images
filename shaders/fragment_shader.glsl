#version 330 core

in vec2 fragmentTexCoord;
out vec4 fragmentColor;

uniform sampler2D imageTexture;

void main()
{
    fragmentColor = texture(imageTexture, fragmentTexCoord);
}