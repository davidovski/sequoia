"""
Forked from:
https://github.com/gabdube/pyshaders/blob/master/pyshaders.py

Modified for inclusion in `trimesh`
----------------------------------------

MIT License

Copyright (c) 2016 Gabriel Dube

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pyglet import gl

from ctypes import (c_char,
                    c_uint,
                    cast,
                    POINTER,
                    pointer,
                    byref)
import weakref
import itertools

from collections import namedtuple
from collections.abc import Sequence


def read_opengl_array(_id, length, fn, ctype=c_char):
    """
    Wrapper to easily read data from functions of this kind
    fn(identifier, buffer_lenght_in, buffer_length_out, buffer)
    """
    global out_buffer_length
    buffer = (ctype * length)()
    buffer_ptr = cast(buffer, POINTER(ctype))
    fn(_id, length, byref(gl.GLint(0)), buffer_ptr)
    return buffer


def shader_source(data):
    """
    Convert a python string into a **gl.GLchar
    i.e. a pointer to an array of array of gl.GLchar
    """
    if not isinstance(data, bytes):
        raise TypeError('Shader source must be bytes')

    data_len = len(data) + 1
    arr = (c_char * data_len)(*data)
    arr_ptr = cast(arr, POINTER(c_char))

    return pointer(arr_ptr)


TRANSPOSE_MATRIX = True


def transpose_matrices(val):
    global TRANSPOSE_MATRIX
    TRANSPOSE_MATRIX = bool(val)


GETTERS = {
    gl.GLfloat: gl.glGetUniformfv,
    gl.GLint: gl.glGetUniformiv
}

UNIFORMS_DATA = {
    # TypeIndentifier: (c_type, buffer_length, setter, [matrix_size])
    gl.GL_FLOAT: (gl.GLfloat, 1, gl.glUniform1fv),
    gl.GL_FLOAT_VEC2: (gl.GLfloat, 2, gl.glUniform2fv),
    gl.GL_FLOAT_VEC3: (gl.GLfloat, 3, gl.glUniform3fv),
    gl.GL_FLOAT_VEC4: (gl.GLfloat, 4, gl.glUniform4fv),
    gl.GL_INT: (gl.GLint, 1, gl.glUniform1iv),
    gl.GL_INT_VEC2: (gl.GLint, 2, gl.glUniform2iv),
    gl.GL_INT_VEC3: (gl.GLint, 3, gl.glUniform3iv),
    gl.GL_INT_VEC4: (gl.GLint, 4, gl.glUniform4iv),
    gl.GL_FLOAT_MAT2: (gl.GLfloat, 4,
                       lambda x, y, z: gl.glUniformMatrix2fv(
                           x, y, TRANSPOSE_MATRIX, z), (2, 2)),
    gl.GL_FLOAT_MAT3: (gl.GLfloat, 9,
                       lambda x, y, z: gl.glUniformMatrix3fv(
                           x, y, TRANSPOSE_MATRIX, z), (3, 3)),
    gl.GL_FLOAT_MAT4: (gl.GLfloat, 16,
                       lambda x, y, z: gl.glUniformMatrix4fv(
                           x, y, TRANSPOSE_MATRIX, z), (4, 4)),
    gl.GL_FLOAT_MAT2x3: (gl.GLfloat, 6,
                         lambda x, y, z: gl.glUniformMatrix2x3fv(
                             x, y, TRANSPOSE_MATRIX, z), (2, 3)),
    gl.GL_FLOAT_MAT2x4: (gl.GLfloat, 8,
                         lambda x, y, z: gl.glUniformMatrix2x4fv(
                             x, y, TRANSPOSE_MATRIX, z), (2, 4)),
    gl.GL_FLOAT_MAT3x2: (gl.GLfloat, 6,
                         lambda x, y, z: gl.glUniformMatrix3x2fv(
                             x, y, TRANSPOSE_MATRIX, z), (3, 2)),
    gl.GL_FLOAT_MAT3x4: (gl.GLfloat, 12,
                         lambda x, y, z: gl.glUniformMatrix3x4fv(
                             x, y, TRANSPOSE_MATRIX, z), (3, 4)),
    gl.GL_FLOAT_MAT4x2: (gl.GLfloat, 8,
                         lambda x, y, z: gl.glUniformMatrix4x2fv(
                             x, y, TRANSPOSE_MATRIX, z), (4, 2)),
    gl.GL_FLOAT_MAT4x3: (gl.GLfloat, 12,
                         lambda x, y, z: gl.glUniformMatrix4x3fv(
                             x, y, TRANSPOSE_MATRIX, z), (4, 3))
}

UNPACK_ARRAY = [gl.GL_FLOAT, gl.GL_INT]


def to_seq(x): return x if isinstance(x, Sequence) else [x]


def as_matrix(values, size):
    """
    Transform a flat list into a matrix
    """
    row, col = size
    mat = [[] for i in range(row)]

    if row == col:
        for i, v in enumerate(values):
            mat[i % row].append(v)
    else:
        mat_ = [[] for i in range(col)]
        for i, v in enumerate(values):
            mat_[i % col].append(v)

        for i, v in enumerate(itertools.chain.from_iterable(mat_)):
            mat[i // col].append(v)

    return tuple([tuple(i) for i in mat])


def create_uniform_getter(loc, type, count, is_array):
    """
    Create a function that gets uniform values
    """
    if type not in UNIFORMS_DATA.keys():
        return lambda x: None

    c_type, bcount, setter, *mat_size = UNIFORMS_DATA[type]
    c_buf_type = c_type * bcount

    getter = GETTERS[c_type]

    one_val = bcount == 1
    is_matrix = len(mat_size) == 1

    if not is_array and not is_matrix:
        def getter_fn(pid):
            buf = c_buf_type()
            buf_ptr = cast(buf, POINTER(c_type))
            getter(pid, loc, buf_ptr)
            return buf[0] if one_val else tuple(buf)
    elif is_matrix and not is_array:
        def getter_fn(pid):
            buf = c_buf_type()
            buf_ptr = cast(buf, POINTER(c_type))
            getter(pid, loc, buf_ptr)
            return as_matrix(buf, mat_size[0])
    elif is_array and not is_matrix:
        def getter_fn(pid):
            values = []
            buf = c_buf_type()
            buf_ptr = cast(buf, POINTER(c_type))
            for i in range(count):
                # Not sure if loc+1 is super legal, but it works.
                getter(pid, loc.value + i, buf_ptr)
                values.append(buf[0] if one_val else tuple(buf))

            return tuple(values)
    else:
        def getter_fn(pid):
            values = []
            buf = c_buf_type()
            buf_ptr = cast(buf, POINTER(c_type))
            for i in range(count):
                # Not sure if loc+1 is super legal, but it works.
                getter(pid, loc.value + i, buf_ptr)
                values.append(as_matrix(buf, mat_size[0]))

            return tuple(values)

    return getter_fn


def create_uniform_setter(loc, type, count, is_array):
    """
    Generate a function that set an uniform.
    """
    if type not in UNIFORMS_DATA.keys():
        return lambda x: None

    c_type, bcount, setter, *mat_size = UNIFORMS_DATA[type]
    c_buf_type = c_type * (bcount * count)
    is_matrix = len(mat_size) == 1

    if not is_array and not is_matrix:
        def setter_fn(value):
            data = c_buf_type(*to_seq(value))
            data_ptr = cast(data, POINTER(c_type))
            setter(loc, count, data_ptr)

    elif is_array ^ is_matrix:
        unpack = False if type in UNPACK_ARRAY else True

        def setter_fn(value):
            flat = value if not unpack else list(
                itertools.chain.from_iterable(value))
            data = c_buf_type(*flat)
            data_ptr = cast(data, POINTER(c_type))
            setter(loc, count, data_ptr)

    else:
        # for arrays of matrices
        def setter_fn(value):
            flat = [list(itertools.chain.from_iterable(mat)) for mat in value]
            flat = list(itertools.chain.from_iterable(flat))
            data = c_buf_type(*flat)
            data_ptr = cast(data, POINTER(c_type))
            setter(loc, count, data_ptr)

    return setter_fn


class ShaderCompilationError(Exception):
    __slots__ = []

    def __init__(self, logs):
        self.logs = logs

    def __str__(self):
        return "Shaders Errors: \n\n" + self.logs


class PyShadersExtensionError(Exception):
    __slots__ = []


class GLGetObject(object):
    """
        Descriptor that wraps gl.glGet* function
    """
    __slots__ = ['pname']
    buffer = gl.GLint(0)

    def __init__(self, pname): self.pname = pname

    def __set__(self): raise AttributeError('Attribute is not writable')

    def __delete__(self): raise AttributeError('Attribute cannot be deleted')


class GetShaderObject(GLGetObject):
    __slots__ = []

    def __get__(self, instance, cls):
        gl.glGetShaderiv(instance.sid, self.pname, byref(self.buffer))
        return self.buffer.value


class GetProgramObject(GLGetObject):
    __slots__ = []

    def __get__(self, instance, cls):
        gl.glGetProgramiv(instance.pid, self.pname, byref(self.buffer))
        return self.buffer.value


class GetAttributeObject(GLGetObject):
    __slots__ = []

    def __get__(self, instance, cls):
        gl.glGetVertexAttribiv(instance.loc, self.pname, byref(self.buffer))
        return self.buffer.value


class ShaderObject(object):
    """
    Represent a shader object. This wrapper can be used to get
    information about a shader object.

    Slots
        sid: Underlying opengl shader id.
        owned: If the object owns the underlying shader
    """
    __slots__ = ['sid', 'owned']

    type = GetShaderObject(gl.GL_SHADER_TYPE)
    delete_status = GetShaderObject(gl.GL_DELETE_STATUS)
    compiled = GetShaderObject(gl.GL_COMPILE_STATUS)
    log_length = GetShaderObject(gl.GL_INFO_LOG_LENGTH)
    source_length = GetShaderObject(gl.GL_SHADER_SOURCE_LENGTH)

    def __init__(self, shader_id, owned=False):
        """
        Wrap an existing shader object.

        params:
          shader_id: Shader id. Either a python int or a c_[u]int.
          owned: If the object should own the underlying buffer
        """
        self.sid = c_uint(getattr(shader_id, 'value', shader_id))
        self.owned = owned

    @staticmethod
    def __alloc(cls, shader_type):
        sobj = super().__new__(cls)
        sobj.sid = c_uint(gl.glCreateShader(shader_type))
        sobj.owned = True
        return sobj

    @classmethod
    def vertex(cls):
        """
        Class method, create a new uninitialized vertex shader.
        The shaderobject owns the gl.gl resource.
        """
        return ShaderObject.__alloc(cls, gl.GL_VERTEX_SHADER)

    @classmethod
    def fragment(cls):
        """
        Class method, create a new uninitialized fragment shader
        The shaderobject owns the gl.gl resource.
        """
        return ShaderObject.__alloc(cls, gl.GL_FRAGMENT_SHADER)

    @property
    def source(self):
        src = read_opengl_array(
            self.sid,
            self.source_length,
            gl.glGetShaderSource)
        return bytes(src).decode('UTF-8')

    @source.setter
    def source(self, src):
        gl.glShaderSource(
            self.sid, 1, shader_source(
                src.encode('UTF-8')), None)

    @property
    def logs(self):
        """
        Return the compilation log of the shader
        """
        logs = read_opengl_array(
            self.sid,
            self.log_length,
            gl.glGetShaderInfoLog)
        return bytes(logs).decode('UTF-8')

    def compile(self):
        """
        Compile the shader. Return True if the compilation was successful,
        false other wise
        """

        gl.glCompileShader(self.sid)
        return self.compiled == gl.GL_TRUE

    def valid(self):
        """
        Check if the underlying shader is valid.
        Return True if it is, False otherwise.
        """
        return gl.glIsShader(self.sid) == gl.GL_TRUE

    def __bool__(self):
        return self.valid()

    def __eq__(self, other):
        if not isinstance(other, ShaderObject):
            return False

        return self.sid.value == other.sid.value

    def __repr__(self):
        return "ShaderObject {}".format(self.sid)

    def __del__(self):
        if self.owned and self.valid():
            gl.glDeleteShader(self.sid)


class ShaderAccessor(object):
    """
    Allow pythonic access to shader uniforms and shader attributes
    This object is created with a shaderprogram and should not be
    instanced manually.

    Slots:
        prog: Weakref to the uniforms shader program
        cache: Data about the attributes
        cache_type: Type of data in cache
    """

    __slots__ = ['prog', 'cache_type', 'cache']

    def __init__(self, program):
        self.prog = weakref.ref(program)
        self.cache = {}

    def reload(self, maxlength, count, fn, locfn):
        """
            Template to reload a cache of uniforms or attributes
        """
        prog = self.prog()
        if prog is None:
            raise RuntimeError('Shader was freed')

        maxlength = getattr(prog, maxlength)
        name_buf = (c_char * maxlength)()
        name_buf_ptr = cast(name_buf, POINTER(c_char))
        type_buf = gl.GLenum(0)
        name_buf_length = gl.GLint(0)
        buf_size = gl.GLint(0)

        self.cache = {}
        for i in range(getattr(prog, count)):
            fn(prog.pid, i, maxlength, byref(name_buf_length),
               byref(buf_size), byref(type_buf), name_buf_ptr)

            type = type_buf.value
            name_len = name_buf_length.value
            name = bytes(name_buf)[0:name_len].decode('UTF-8')
            size = buf_size.value

            # Kept in a c_int to quickly send the value when setting
            loc = gl.GLint(locfn(prog.pid, name_buf_ptr))

            self.cache_item_build(loc, size, name, type)

    def cache_item_build(self):
        raise NotImplementedError("Should be implemented in a subclass")

    def __iter__(self):
        " Iterate over the Uniform cached in the object. "
        for name, data in self.cache.items():
            yield name, data

    def __len__(self):
        " Return the number of uniforms in the program "
        return len(self.cache)

    def __getitem__(self, key):
        info = self.cache.get(key)
        if info is None:
            raise IndexError('Key {} not found'.format(key))

        return info

    def __contains__(self, item):
        if isinstance(item, self.cache_type):
            return item in self.cache.values()
        elif isinstance(item, str):
            return item in self.cache.keys()
        else:
            return False

    def __repr__(self):
        return str(list(self.cache.keys()))


class ShaderAttribute(object):
    """
    Represent a shader attribute.

    Slots:
      loc: Index of the attribute
      type: Type of the attribute
      name: Name of the attribute
    """
    __slots__ = ['loc', 'type', 'name']

    buffer = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING)
    enabled = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_ENABLED)
    stride = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_STRIDE)
    normalized = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_NORMALIZED)
    size = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_SIZE)
    ptr_type = GetAttributeObject(gl.GL_VERTEX_ATTRIB_ARRAY_TYPE)

    def enable(self):
        " Enable the shader attribute "
        gl.glEnableVertexAttribArray(self.loc)

    def disable(self):
        " Disable the shader attribute "
        gl.glDisableVertexAttribArray(self.loc)

    def point_to(self, offset, type, size, normalized=False, stride=0):
        """
        Call gl.glVertexAttribPointer with the supplied parameters. The attributes
        "type" and "size" are handled by the library. Attrbute shader must be in use.

        Parameters
        -------------
        offset : int
          Offset of the data in bytes
        type :
          Type of the pointed data. Must be a gl.GL_* constant such as gl.GL_FLOAT.
        size : int
          Specifies the number of components per generic vertex attribute
          Must be 1, 2, 3, or 4.
        normalized: bool
          Specifies whether fixed-point data values should be normalized
          (True) or converted directly as fixed-point values (gl.GL_FALSE)
        stride : int
          Specifies the byte offset between consecutive generic vertex attributes.
        """
        gl.glVertexAttribPointer(
            self.loc, size, type, normalized, stride, offset)


class ShaderAttributeAccessor(ShaderAccessor):
    """
    Allow pythonic access to a shader attributes.
    This object is created with a shaderprogram and should not be
    instanced manually.
    """

    def __init__(self, program):
        super().__init__(program)
        self.cache_type = ShaderAttribute

    def cache_item_build(self, loc, size, name, type):
        """
        Add an item to the cache. This is called by reload.
        """
        attribinfo = ShaderAttribute()
        attribinfo.loc = gl.GLuint(loc.value)
        attribinfo.type = type
        attribinfo.name = name

        self.cache[name] = attribinfo

    def reload(self):
        """
        Reload or build for the first time the attribute cache.
        This can be quite expensive so it is only done on shader linking.
        If the shader was linked outside the api, you have to call this manually.
        """
        super().reload('max_attribute_length', 'attributes_count',
                       gl.glGetActiveAttrib, gl.glGetAttribLocation)

    def __getattr__(self, name):
        return self[name]


class ShaderUniformAccessor(ShaderAccessor):
    """
    Allow pythonic access to a shader uniforms.
    This object is created with a shaderprogram and should not be
    instanced manually.
    """

    __slots__ = []

    uinfo = namedtuple(
        'Uniform', [
            'loc', 'type', 'size', 'name', 'get', 'set'])

    def __init__(self, program):
        super().__init__(program)
        self.cache_type = ShaderUniformAccessor.uinfo

    def cache_item_build(self, loc, size, name, type):
        """
        Add an item to the cache. This is called by reload.
        """
        # Arrays name ends with [0]. Ex: 'int[5] foo' name is 'foo[0]'
        if size == 1 and '[0]' not in name:
            is_array = False
        else:
            name = name.replace('[0]', '')
            is_array = True

        set = create_uniform_setter(loc, type, size, is_array)
        get = create_uniform_getter(loc, type, size, is_array)

        uinfo = self.uinfo(loc=loc, type=type, name=name, size=size,
                           get=get, set=set)
        self.cache[name] = uinfo

    def reload(self):
        """
        Reload or build for the first time the uniforms cache.
        This can be quite expensive so it is only done on shader linking.
        If the shader was linked outside the api, you have to call this manually.
        """
        super().reload('max_uniform_length', 'uniforms_count',
                       gl.glGetActiveUniform, gl.glGetUniformLocation)

    def __getattr__(self, name):

        if name in self.cache.keys():
            prog = self.prog()
            if prog is None:
                raise RuntimeError('Shader was freed')
            return self.cache.get(name).get(prog.pid)

        raise AttributeError('No uniform named "{}" found'.format(name))

    def __setattr__(self, name, value):
        if name in ShaderAccessor.__slots__:
            return object.__setattr__(self, name, value)
        elif name in self.cache.keys():
            return self.cache.get(name).set(value)

        raise AttributeError(
            'No attribute/uniform named "{}" found'.format(name))


class ShaderProgram(object):
    """
    Represent a shader program. This wrapper can be used to get information
    about a shader program. It can also be used to get and set uniforms value
    of the shader

    Slots:
        pid: Underlying opengl.gl program id.
        owned: If the object own the underlying buffer
        uniforms: Uniforms collection of the shader
        attributes: Attributes collection of the shader
    """

    delete_status = GetProgramObject(gl.GL_DELETE_STATUS)
    log_length = GetProgramObject(gl.GL_INFO_LOG_LENGTH)
    link_status = GetProgramObject(gl.GL_LINK_STATUS)
    validate_status = GetProgramObject(gl.GL_VALIDATE_STATUS)
    shaders_count = GetProgramObject(gl.GL_ATTACHED_SHADERS)
    attributes_count = GetProgramObject(gl.GL_ACTIVE_ATTRIBUTES)
    uniforms_count = GetProgramObject(gl.GL_ACTIVE_UNIFORMS)
    max_attribute_length = GetProgramObject(gl.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    max_uniform_length = GetProgramObject(gl.GL_ACTIVE_UNIFORM_MAX_LENGTH)

    __slots__ = ['pid', 'owned', 'uniforms', 'attributes', '__weakref__']

    def __init__(self, program_id, owned=False):
        """
        Wrap an existing shader program.

        *program_id*: Program id. Either a python int or a c_[u]int.
        *owned*: If the object should own the underlying buffer
        """
        self.pid = c_uint(getattr(program_id, 'value', program_id))
        self.uniforms = ShaderUniformAccessor(self)
        self.attributes = ShaderAttributeAccessor(self)
        self.owned = owned

    @classmethod
    def new_program(cls):
        """
        Create a new program. The object own the ressources
        """
        pobj = super().__new__(cls)
        pobj.pid = c_uint(gl.glCreateProgram())
        pobj.uniforms = ShaderUniformAccessor(pobj)
        pobj.attributes = ShaderAttributeAccessor(pobj)
        pobj.owned = True
        return pobj

    @property
    def logs(self):
        """
        Return the compilation log of the program
        """
        logs = read_opengl_array(
            self.pid,
            self.log_length,
            gl.glGetProgramInfoLog)
        return bytes(logs).decode('UTF-8')

    def attach(self, *objs):
        """
        Attach shader objects to the program.
        Objs must be a list of ShaderObject.

        Ownership of the underlying shaders is transferred to the program .
        """
        for obj in objs:
            gl.glAttachShader(self.pid, obj.sid)
            obj.owned = False

    def detach(self, *objs, delete=True):
        """
        Detach shader objects from the program.
        Objs must be a list of ShaderObject.

        Keyword argument:
            delete: If the detached shaders should be marked for destruction
        """
        for obj in objs:
            gl.glDetachShader(self.pid, obj.sid)
            obj.owned = delete

    def valid(self):
        """
        Check if the underlying program is valid.
        Return True if it is, False otherwise.
        """
        return gl.glIsProgram(self.pid) == gl.GL_TRUE

    def link(self):
        """
        Link the shader program. Return True if the linking was successful,
        False otherwise.
        Also reload the uniform cache is successful
        """
        gl.glLinkProgram(self.pid)
        if self.link_status == gl.GL_TRUE:
            self.uniforms.reload()
            self.attributes.reload()
            return True

    def shaders(self):
        """
        Return a list of shader objects linked to the program.
        The returned shader objects do not own the underlying shader.
        """
        shaders = read_opengl_array(
            self.pid,
            self.shaders_count,
            gl.glGetAttachedShaders,
            c_uint)
        return [ShaderObject(sid) for sid in shaders]

    def use(self):
        " Use the shader program "
        gl.glUseProgram(self.pid)

    def enable_all_attributes(self):
        " Call enable() on the shader attributes "

        for name, attr in self.attributes:
            attr.enable()

    def disable_all_attributes(self):
        " Call disable() on the shader attributes "

        for name, attr in self.attributes:
            attr.disable()

    @staticmethod
    def clear():
        " Remove the current shader program "
        gl.glUseProgram(0)

    def __bool__(self):
        return self.valid()

    def __eq__(self, other):
        if not isinstance(other, ShaderProgram):
            return False

        return self.pid.value == other.pid.value

    def __repr__(self):
        return "ShaderProgram {}".format(self.pid)

    def __del__(self):
        try:
            if self.owned and self.valid():
                # Detach and mark for deletion all attahed shader object
                self.detach(*self.shaders())
                gl.glDeleteProgram(self.pid)
        except ImportError:
            # raised when python is shutting down
            pass


def current_program():
    """
        Return the currently bound shader program or None if there is None.
        The returned shader do not own the underlying buffer.
    """
    cprog = gl.GLint(0)
    gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, byref(cprog))
    if cprog.value == 0:
        return None
    else:
        return ShaderProgram(cprog)


def from_string(verts, frags):
    """
    High level loading function.

    Load a shader using sources passed in sequences of string.
    Each source is compiled in a shader unique shader object.
    Return a linked shaderprogram. The shaderprogram owns the gl.gl resource.

    verts: Sequence of vertex shader sources
    frags: Sequence of fragment shader sources
    """
    if isinstance(verts, str):
        verts = (verts,)
    if isinstance(frags, str):
        frags = (frags,)

    logs, objs = "", []

    for src in verts:
        vert = ShaderObject.vertex()
        vert.source = src
        objs.append(vert)

    for src in frags:
        frag = ShaderObject.fragment()
        frag.source = src
        objs.append(frag)

    for obj in objs:
        if obj.compile() is False:
            logs += obj.logs

    if len(logs) == 0:
        prog = ShaderProgram.new_program()
        prog.attach(*objs)
        if not prog.link():
            raise ShaderCompilationError(prog.logs)

        return prog

    raise ShaderCompilationError(logs)