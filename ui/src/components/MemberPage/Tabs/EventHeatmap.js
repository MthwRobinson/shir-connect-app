import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import CalendarHeatmap from 'react-calendar-heatmap';
import ReactTooltip from 'react-tooltip';

import moment from 'moment';

import 'react-calendar-heatmap/dist/styles.css';

class EventHeatmaps extends Component {
  selectEvent = (eventID) => {
    // Switches to the participant page
    const url = '/event?id='+ eventID; 
    this.props.history.push(url);
  }

  render(){
    const member = this.props.member;
    let values = {};
    for(let i=0; i<member.events.length; i++){
      const event = member.events[i];
      const year = moment(event.start_datetime).format('YYYY');
      const start = moment(event.start_datetime).format('YYYY-MM-DD');
      const value = {
        date: start,
        eventId: event.event_id,
        name: event.name
      }
      if(year in values){
        values[year].push(value);
      } else {
        values[year] = [value];
      }
    }

    return (
      <div>
        {Object.keys(values).reverse().map((year, index) => {
          const startDate = moment(new Date(year + '-01-01'))
            .add(-1, 'days');
          const endDate = moment(startDate)
            .add(1, 'years')
            .format('YYYY-MM-DD');
          return(
            <div>
              <h4>{year}</h4>
              <CalendarHeatmap
                startDate={startDate}
                endDate={endDate}
                values={values[year]}
                onClick={(value) => this.selectEvent(value.eventId)}

                tooltipDataAttrs={value => {
                  if(value.name){
                    return {
                      'data-tip': `Attended ${value.name} on ${value.date}`
                    };
                  }
                }}
              />
              <ReactTooltip />
            </div>
          )
        })}
      </div> 
    )
  }
};
export default withRouter(EventHeatmaps);
