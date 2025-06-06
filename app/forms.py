
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    nombre_usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class ProductoForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    categoria_id = SelectField('Categoría', coerce=int, validators=[Optional()])  # Opción de categorías
    precio_costo = FloatField('Precio de Compra', validators=[DataRequired(), NumberRange(min=0)])
    precio_venta = FloatField('Precio de Venta', validators=[DataRequired(), NumberRange(min=0)])
    stock_minimo = IntegerField('Stock Mínimo', default=0, validators=[NumberRange(min=0)])
    stock_actual = IntegerField('Stock Actual', default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('Guardar')