import moment from 'moment';
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

class QuickFacts extends Component {
  render(){
    const event = this.props.event;
    const start = moment(this.props.event.start_datetime);
    const end = moment(this.props.event.end_datetime);

    let address = '';
    if(event.address_1){
      address += event.address_1;
      if(event.city){
        address += ', ' + event.city;
      }
      if(event.region){
        address += ', ' + event.region;
      }
      if(event.postal_code){
        address += ', ' + event.postal_code;
      }
    }

    let attendeeCount = 0;
    if(event.attendee_count > 0){
      attendeeCount = event.attendee_count;
    }

    return(
      <div className='quick-facts'>
        <ul>
          <li><b>Time: </b> 
            {start.format('MM/DD/YY, h:MM a')}-
            {end.format('MM/DD/YY, h:MM a')}
          </li>
          <li><b>Registered:</b> {attendeeCount}/{event.capacity} </li>
          <li><b>Venue:</b> {event.venue_name != null
              ? event.venue_name : 'Temple Rodef Shalom'}
          </li>
          <li><b>Location:</b> {address.length>0
              ? address : 'Not Available'}
          </li>
          <li><b>Description:</b> {event.description}</li>
        </ul>
      </div> 
    )
  }
};
export default withRouter(QuickFacts);
