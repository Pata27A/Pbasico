
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, RadioField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    nombre_usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')



class ProductoForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired(), Length(max=50)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=150)])
    categoria_id = SelectField('Categoría', coerce=int)
    precio_costo = FloatField('Precio Costo', validators=[DataRequired()])
    precio_venta = FloatField('Precio Venta', validators=[DataRequired()])
    stock_minimo = IntegerField('Stock Mínimo', default=0)
    stock_actual = IntegerField('Stock Actual', default=0)
    
    iva_tipo = RadioField(
        'Tipo de IVA',
        choices=[('10', 'IVA 10%'), ('05', 'IVA 5%'), ('EX', 'Exenta')],
        default='10',
        validators=[DataRequired()]
    )

    submit = SubmitField('Guardar')
