import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Rapidtrans S.A.",
    page_icon="💰",
    layout="wide",
)

# Crear un contenedor con fondo gris
header_container = st.container(border=1)
header_container.markdown(
    """
    <style>
    .header-container {
        background-color: silver !important;
        color: silver;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Agregar contenido al contenedor
with header_container:
    logo, cabecera = st.columns([0.1, 0.9])
    with cabecera:
        st.write("<h1 style='text-align: right; color: blue'>Rapidtrans S.A.</h1>", unsafe_allow_html=True)
    with logo:
        st.image("logo_r.png", use_column_width="auto")

# Crear o conectar a la base de datos
conn = sqlite3.connect('chat.db')
c = conn.cursor()

# Crear la tabla de usuarios si no existe
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL,
            contraseña TEXT NOT NULL)''')

# Crear la tabla de publicaciones si no existe
c.execute('''CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            usuario TEXT NOT NULL,
            publicación TEXT NOT NULL)''')

# Crear la tabla de mensajes si no existe
c.execute('''CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            usuario TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            mensaje TEXT NOT NULL)''')

# Página inicial
# Aquí deberías incluir el código para el registro, inicio de sesión y visualización de Mensajes y publicaciones.
def registro():
    # Conectar a la base de datos y crear un cursor
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    with st.form("register_form"):
        nombre = st.text_input("Nombre")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña")
        if st.form_submit_button("Registrarse") and nombre != "" and usuario != "" and contraseña != "":
            # Ejecutar una consulta SQL para verificar si el usuario ya está registrado
            c.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,))
            result = c.fetchone()

            # Procesar el resultado de la consulta
            if result:
                st.error('El usuario ya está registrado')
            else:
                # Ejecutar una consulta SQL para insertar el nuevo usuario
                c.execute('INSERT INTO usuarios (nombre, usuario, contraseña) VALUES (?, ?, ?)', (nombre, usuario, contraseña))
                conn.commit()
                st.success('Usuario registrado correctamente')
                st.session_state["nombre"] = nombre
                st.session_state["usuario"] = usuario
                st.rerun()
            # Cerrar la conexión a la base de datos
            conn.close()
        else:
            st.error("No puedes dejar campos en blanco")

# Función para cerrar sesión
def cerrar_sesion():
    # Remover el nombre de usuario de la sesión
    del st.session_state['usuario']
    st.rerun()

def login():
    # Conectar a la base de datos y crear un cursor
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    # Obtener los valores ingresados por el usuario
    with st.form("login_form"):
        usuario = st.text_input("Usuario ")
        contraseña = st.text_input("Contraseña ", type="password")
        if st.form_submit_button("Ingresar"):
            # Ejecutar una consulta SQL para verificar las credenciales
            c.execute('SELECT * FROM usuarios WHERE usuario = ? AND contraseña = ?', (usuario, contraseña))
            result = c.fetchone()
            # Procesar el resultado de la consulta
            if result:
                st.success('Inicio de sesión exitoso')
                st.session_state["nombre"] = result[1]
                st.session_state["usuario"] = result[2]
                st.rerun()
            else:
                st.error('Credenciales incorrectas')

    # Cerrar la conexión a la base de datos
    conn.close()

# Función para obtener todos los mensajes de la base de datos
def obtener_mensajes():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM mensajes ORDER BY id DESC')
    mensajes = c.fetchall()
    conn.close()
    return mensajes

# Función para agregar un nuevo mensaje a la base de datos
def agregar_mensaje(mensaje, usuario, destinatario):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO mensajes (fecha, usuario, destinatario, mensaje) VALUES (datetime("now"), ?, ?, ?)', (usuario, destinatario, mensaje))
    conn.commit()
    conn.close()

def eliminar_mensaje(id_mensaje):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM mensajes WHERE id = ?', (id_mensaje,))
    conn.commit()
    conn.close()

# Función para obtener todas las publicaciones de la base de datos
def obtener_publicaciones():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM publicaciones ORDER BY id DESC')
    publicaciones = c.fetchall()
    conn.close()
    return publicaciones

# Función para agregar una nueva publicación a la base de datos
def agregar_publicacion(mensaje, usuario):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO publicaciones (fecha, usuario, publicación) VALUES (datetime("now"), ?, ?)', (usuario, mensaje))
    conn.commit()
    conn.close()

def eliminar_publicacion(id_publicacion):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM publicaciones WHERE id = ?', (id_publicacion,))
    conn.commit()
    conn.close()

def mensajeria():
    usuario = st.session_state["usuario"]
    nombre = st.session_state["nombre"]

    st.header("Servicio de Mensajería Gratuito!")

    st.write(f"Bienvenido {nombre}")
    contenido, private = st.tabs(["Publicaciones", "Private"])
    with contenido:
        st.subheader("Publicaciones")
        with st.container():
            with st.form(key="Publicaciones", clear_on_submit=True):
                # Formulario para agregar una nueva publicación
                mensaje = st.text_area('Escribe tu publicación aqui:')
                st.write(f'Has escrito {len(mensaje)} caracteres.')
                if st.form_submit_button('Enviar Publicación'):
                    agregar_publicacion(mensaje, usuario)
                    st.rerun()
        with st.container(height=750):
            # Mostrar todas las publicaciones en la página
            publicaciones = obtener_publicaciones()
            for publicacion in publicaciones:
                st.write('%s - %s:' % (publicacion[1], publicacion[2]))
                st.write(publicacion[3])

                # Crear un botón para eliminar la publicación
                if publicacion[2] == usuario:
                    if st.button('Eliminar', key=f"eliminar_{publicacion[0]}"):
                        eliminar_publicacion(publicacion[0])  # Llamar a la función para eliminar la publicación
                        st.rerun()
                # Crear un botón para redirigir a la página del enlace
                if 'http' in publicacion[3]:
                    on_click=lambda: st.redirect(publicacion[3])


    with private:
        st.subheader("Mensajería Privada")
        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        destinatario = st.text_input("Destinatario", value="")
        if destinatario != "":
            c.execute('SELECT * FROM usuarios WHERE usuario = ?', (destinatario,))
            user = c.fetchone()
            if user:
                st.write(f"Puedes escribirle a {user[1]}")
            else:
                st.error('Usuario no Registrado')
        with st.form(key="sms_private", clear_on_submit=True):
            # Formulario para agregar una nueva publicación
            mensaje = st.text_area('Escribe un mensaje:', value="")
            st.write(f'Has escrito {len(mensaje)} caracteres.')
            if st.form_submit_button('Enviar'):
                agregar_mensaje(mensaje, usuario, destinatario)
                st.rerun()
        conn.close()
        with st.container(height=500):
            # Mostrar todas las publicaciones en la página
            mensajes = obtener_mensajes()
            for mensaje in mensajes:
                if mensaje[3] == usuario:
                    st.write('%s - %s:' % (mensaje[1], f"R-{mensaje[2]}"))
                    st.write(mensaje[4])
                    # Crear un botón para redirigir a la página del enlace
                    if 'http' in mensaje[4]:
                        on_click=lambda: st.redirect(mensaje[4])
                    # if st.button("Responder", key=f"agregar_{mensaje[0]}"):
                    other, answer = st.tabs(["", "Responder"])
                    with answer:
                        with st.form(key=f"agregar_{mensaje[0]}", clear_on_submit=True):
                            destinatario = mensaje[2]
                            st.write(destinatario)
                            mensaje = st.text_area('Escribe un mensaje:')
                            if st.form_submit_button("Responder"):
                                agregar_mensaje(mensaje, usuario, destinatario)
                                st.write(f"{destinatario} - {mensaje}")
                                st.rerun()
                    with other:
                        st.empty()

                    
                elif mensaje[2] == usuario and mensaje[3] == destinatario:
                    st.write('%s - %s:' % (mensaje[1], f"E-{mensaje[3]}"))
                    st.write(mensaje[4])
                    # Crear un botón para eliminar la publicación
                    if st.button('Eliminar', key=f"eliminar__{mensaje[0]}"):
                        eliminar_mensaje(mensaje[0])  # Llamar a la función para eliminar la publicación
                        st.rerun()
            

def init():
    inicio, about = st.tabs(["Inicio", "Acerca de nosotros"])
    with inicio:
        st.write("## Bienvenidos a mi Página Web! ")
        st.markdown(
            """
            La familia **Rapidtrans S.A.** les da la Bienvenida a nuestro portal Web.  
            Donde podrás comunicarte de la forma más segura de la red. y si eso no es suficiente tambien podras divertirte con las demás opciones de 
            entretenimiento que iremos trayendo a la plataforma.  
            Te adelanto, podras disfrutar de TV totalmente gratuita con los mejores canales por suscripción sin necesidad de pagar por verlos, por ahora puedes verlos desde [aqui](https://rapidtrans.netlify.app/tv), asi como descargar 
            libros en formato PDF totalmente gratuitos, por ahora puedes descargarlos desde [aqui](https://rapidtrans.netlify.app/libros) entre otras opciones.
            """
        )
    with about:
        st.write("## ¿Que es Rapidtrans S.A.? ")
        st.markdown(
            """
            La iniciativa Rapidtrans S.A. nace alrededor del año 2001, como solucion a la necesidad de realizar trabajos de transcripción e investigación
            para las personas que no tenian una computadora disponible o el tiempo requerido para realizar esto. Con el tiempo expandio sus alcances 
            e inicio una nueva etapa con la que ofrecía poner a disposición de las demas personas una computadora de escritorio a precios accesibles
            y en oportunidades hasta pagaderos por cuotas. Con el paso y la evolucion del tiempo nacieron nuevas oportunidades, asi llegamos a la situacion
            actual, donde participamos activamente en diversas ramas de la economía moderna.

            ### Funciones actuales de Rapidtrans S.A.
            - Comercio Electronico de Criptoactivos.
                * Compra y Venta de Criptomonedas, principalmente USDT, BTC, LTC, TRX y DOGE.
                * Farming en Juegos NFTs.
                * Minería en la nube y en paginas PTC y/o faucets.
                * Apuestas en casinos virtuales.
            - Actividades adicionales
                * Ventas de equipos Electronicos, Computadoras de escritorio y laptos, entre otros.
                * Diseño, Elaboración y administración de Paginas Webs.
                * Diseño, Elaboración, asesoramiento y/o supervisión de proyectos de Construcción Civil.
                * El Responsable del caso debe aprobar la respuesta generada por el analista y enviar a la organización.
        """
        )

    st.write("## En las Redes ")
    web, app, x, rapidchat  = st.columns([0.25, 0.25, 0.25, 0.25])
    with web:
        st.write("### Pagina Web")
        st.link_button("Ingresa aqui! - Rapidtrans S.A.", "https://rapidtrans.netlify.app/")

    with app:
        st.write("### INSTAGRAM")
        st.link_button("@Cdmn137", "https://www.instagram.com/cdmn137/")

    with x:
        st.write("### X (Antes Twitter)")
        st.write("Tambien estamos en X!")
        st.link_button("Contactenos por X!", "https://twitter.com/todopoderoso137")

    with rapidchat:
        st.write("### Rapidchat")
        st.link_button("Rapidtrans137", "https://rapidtrans.streamlit.app")

def main():
    if 'usuario' not in st.session_state:
        inicio, ingreso = st.columns([0.75, 0.25])
        with inicio:
            init()
        with ingreso:
            iniciar, registrar = st.tabs(["Iniciar sesión", "Registrarse"])
            with registrar:
                registro()
            with iniciar:
                login()
            with st.container():
                st.write(
                    """
                    Solo necesitas conocer el Usuario de la persona con quien deseas comunicarte. 
                    * Puedes pedirle su usuario y comenzar a escribirle. 
                    * Le puedes enviar tu nombre de usuario a otra persona para que te escriba. 
                    * Sin restricción de contenido.  

                    Asi de sencillo es estar en contacto con otras personas. 
                    """)
    else:
        vacio, salir = st.columns([0.9, 0.1])
        with vacio:
            st.empty()
        with salir:
            st.write(st.session_state["usuario"])
            if st.button("Salir"):
                cerrar_sesion()
        info, publicidad = st.columns([0.75, 0.25])
        with info:
            com, tv = st.tabs(["Mensajería", "TV Gratis"])
            with tv:
                st.write(
                """
                Página en Construcción
                🏗
                """
                )
                st.image("construccion.jpg", use_column_width="auto")
            with com:
                mensajeria()
        with publicidad:
            st.write("Aqui podras publicar tus proyectos!")
            st.image("bitcoin.jpg", use_column_width="auto")


if __name__ == '__main__':
    main()
