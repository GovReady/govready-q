/* eslint-disable warning */
import React from 'react'
import ObjectField from 'react-jsonschema-form/lib/components/fields/ObjectField'
import { retrieveSchema } from 'react-jsonschema-form/lib/utils'
import { Col } from 'react-bootstrap'

export default class LayoutGridField extends ObjectField {
  state = { firstName: 'hasldf' }

  render() {
    const { uiSchema } = this.props
    let { layoutGridSchema } = this.props
    if (!layoutGridSchema) layoutGridSchema = uiSchema['ui:layout_grid']

    if (layoutGridSchema['ui:row']) {
      return this.renderRow(layoutGridSchema)
    } else if (layoutGridSchema['ui:col']) {
      return this.renderCol(layoutGridSchema)
    } else {
      return this.renderField(layoutGridSchema)
    }
  }

  renderRow(layoutGridSchema) {
    const { myKey } = this.props
    const rows = layoutGridSchema['ui:row']

    const group = layoutGridSchema['ui:group']

    if (group) {
      const { fields, formContext } = this.props.registry
      const { TitleField } = fields
      const { required } = this.props
      const title = group && typeof group === 'string' ? group : null

      return (
        <fieldset className="rjsf-layout-grid-group">
          {title ? <TitleField
              title={title}
              required={required}
              formContext={formContext}/> : null}
          {<div className="row" key={myKey}>{this.renderChildren(rows)}</div>}
        </fieldset>
      )
    } else {
      return <div className="row" key={myKey}>{this.renderChildren(rows)}</div>
    }
  }

  renderCol(layoutGridSchema) {
    const { myKey } = this.props
    const { children, ...colProps } = layoutGridSchema['ui:col']

    const group = layoutGridSchema['ui:group']

    if (group) {
      const { fields, formContext } = this.props.registry
      const { TitleField } = fields
      const { required } = this.props
      const title = group && typeof group === 'string' ? group : null

      return (
        <Col {...colProps} key={myKey}>
          <fieldset className="rjsf-layout-grid-group">
            {title ? <TitleField
                title={title}
                required={required}
                formContext={formContext}/> : null}
            {this.renderChildren(children)}
          </fieldset>
        </Col>
      )
    } else {
      return <Col {...colProps} key={myKey}>{this.renderChildren(children)}</Col>
    }
  }

  renderChildren(childrenLayoutGridSchema) {
    const { definitions } = this.props.registry
    const schema = retrieveSchema(this.props.schema, definitions)

    return childrenLayoutGridSchema.map((layoutGridSchema, index) => (
      <LayoutGridField
        {...this.props}
        key={index}
        myKey={index}
        schema={schema}
        layoutGridSchema={layoutGridSchema}/>
    ))
  }

  renderField(layoutGridSchema) {
    const {
      myKey,
      uiSchema,
      errorSchema,
      idSchema,
      disabled,
      readonly,
      onBlur,
      onFocus,
      formData
    } = this.props
    const { definitions, fields } = this.props.registry
    const { SchemaField } = fields
    const schema = retrieveSchema(this.props.schema, definitions)
    let name
    let render
    if (typeof layoutGridSchema === 'string') {
      name = layoutGridSchema
    } else {
      name = layoutGridSchema.name
      render = layoutGridSchema.render
    }

    if (schema.properties[name]) {
      return (
        <SchemaField
          myKey={myKey}
          name={name}
          required={this.isRequired(name)}
          schema={schema.properties[name]}
          uiSchema={uiSchema[name]}
          errorSchema={errorSchema[name]}
          idSchema={idSchema[name]}
          formData={formData[name]}
          onChange={this.onPropertyChange(name)}
          onBlur={onBlur}
          onFocus={onFocus}
          registry={this.props.registry}
          disabled={disabled}
          readonly={readonly}/>
      )
    } else {
      const UIComponent = render || (() => null)

      return (
        <UIComponent
          myKey={myKey}
          name={name}
          formData={formData}
          errorSchema={errorSchema}
          uiSchema={uiSchema}
          schema={schema}
          registry={this.props.registry}
        />
      )
    }
  }
}