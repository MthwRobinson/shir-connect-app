import React, { Component } from 'react';

import './ModuleCard.css';

class ModuleCard extends Component {
  render() {
    return (
      <div onClick={()=>this.props.click()} className="ModuleCard">
        <div className='module-image pullLeft'>
          <i className={this.props.icon}></i>
        </div>
        <div className="module-info pullLeft">
          <h3>{this.props.title}</h3>
          {this.props.bullets.map((bullet, index) => {
            return(
              <div>
                <b>{bullet}</b><br/>
              </div>
            )
          })}
        </div>
      </div>
    );
  }
}

export default ModuleCard;
